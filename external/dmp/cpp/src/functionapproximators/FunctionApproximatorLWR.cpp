/**
 * @file   FunctionApproximatorLWR.cpp
 * @brief  FunctionApproximatorLWR class source file.
 * @author Freek Stulp
 */

#include "functionapproximators/FunctionApproximatorLWR.h"

#include "functionapproximators/ModelParametersLWR.h"
#include "functionapproximators/MetaParametersLWR.h"

#include <iostream>
#include <eigen3/Eigen/SVD>
#include <eigen3/Eigen/LU>

using namespace std;
using namespace Eigen;

FunctionApproximatorLWR::FunctionApproximatorLWR(MetaParametersLWR *meta_parameters, ModelParametersLWR *model_parameters) 
:
  FunctionApproximator(meta_parameters,model_parameters)
{
}

FunctionApproximatorLWR::FunctionApproximatorLWR(ModelParametersLWR *model_parameters) 
:
  FunctionApproximator(model_parameters)
{
}


FunctionApproximator* FunctionApproximatorLWR::clone(void) const {

  MetaParametersLWR*  meta_params  = NULL;
  if (getMetaParameters()!=NULL)
    meta_params = dynamic_cast<MetaParametersLWR*>(getMetaParameters()->clone());

  ModelParametersLWR* model_params = NULL;
  if (getModelParameters()!=NULL)
    model_params = dynamic_cast<ModelParametersLWR*>(getModelParameters()->clone());

  if (meta_params==NULL)
    return new FunctionApproximatorLWR(model_params);
  else
    return new FunctionApproximatorLWR(meta_params,model_params);
};



/** Compute Moore-Penrose pseudo-inverse. 
 * Taken from: http://eigen.tuxfamily.org/bz/show_bug.cgi?id=257
 * \param[in]  a       The matrix to be inversed.
 * \param[out] result  The pseudo-inverse of the matrix.
 * \param[in]  epsilon Don't know, not my code ;-)
 * \return     true if pseudo-inverse possible, false otherwise
 */
template<typename _Matrix_Type_>
bool pseudoInverse(const _Matrix_Type_ &a, _Matrix_Type_ &result, double
epsilon = std::numeric_limits<typename _Matrix_Type_::Scalar>::epsilon())
{
  if(a.rows()<a.cols())
      return false;

  Eigen::JacobiSVD< _Matrix_Type_ > svd = a.jacobiSvd(Eigen::ComputeThinU |
Eigen::ComputeThinV);

  typename _Matrix_Type_::Scalar tolerance = epsilon * std::max(a.cols(),
a.rows()) * svd.singularValues().array().abs().maxCoeff();

  result = svd.matrixV() * _Matrix_Type_( (svd.singularValues().array().abs() >
tolerance).select(svd.singularValues().
      array().inverse(), 0) ).asDiagonal() * svd.matrixU().adjoint();
      
  return true;
}


void FunctionApproximatorLWR::train(const MatrixXd& inputs, const MatrixXd& targets)
{
  if (isTrained())  
  {
    cerr << "WARNING: You may not call FunctionApproximatorLWR::train more than once. Doing nothing." << endl;
    cerr << "   (if you really want to retrain, call reTrain function instead)" << endl;
    return;
  }
  
  assert(inputs.rows() == targets.rows());
  assert(inputs.cols()==getExpectedInputDim());

  const MetaParametersLWR* meta_parameters_lwr = 
    dynamic_cast<const MetaParametersLWR*>(getMetaParameters());
  
  VectorXd min = inputs.colwise().minCoeff();
  VectorXd max = inputs.colwise().maxCoeff();
  
  MatrixXd centers, widths, activations;
  meta_parameters_lwr->getCentersAndWidths(min,max,centers,widths);
  ModelParametersLWR::normalizedKernelActivations(centers,widths,inputs,activations);
  
  // Make the design matrix
  MatrixXd X = MatrixXd::Ones(inputs.rows(),inputs.cols()+1);
  X.leftCols(inputs.cols()) = inputs;
  
  
  int n_kernels = activations.cols();
  int n_betas = X.cols(); 
  int n_samples = X.rows(); 
  MatrixXd W;
  MatrixXd beta(n_kernels,n_betas);
  
  double epsilon = 0.000001*activations.maxCoeff();
  for (int bb=0; bb<n_kernels; bb++)
  {
    VectorXd W_vec = activations.col(bb);
    
    if (epsilon==0)
    {
      // Use all data
      
      W = W_vec.asDiagonal();
      // Compute beta
      // 1 x n_betas 
      // = inv( (n_betas x n_sam)*(n_sam x n_sam)*(n_sam*n_betas) )*( (n_betas x n_sam)*(n_sam x n_sam)*(n_sam * 1) )   
      // = inv(n_betas x n_betas)*(n_betas x 1)
      VectorXd cur_beta = (X.transpose()*W*X).inverse()*X.transpose()*W*targets;
      beta.row(bb)   =    cur_beta;
    } 
    else
    {
      // Very low weights do not contribute to the line fitting
      // Therefore, we can delete the rows in W, X and targets for which W is small
      //
      // Example with epsilon = 0.1 (a very high value!! usually it will be lower)
      //    W =       [0.001 0.01 0.5 0.98 0.46 0.01 0.001]^T
      //    X =       [0.0   0.1  0.2 0.3  0.4  0.5  0.6 ; 
      //               1.0   1.0  1.0 1.0  1.0  1.0  1.0  ]^T  (design matrix, so last column = 1)
      //    targets = [1.0   0.5  0.4 0.5  0.6  0.7  0.8  ]
      //
      // will reduce to
      //    W_sub =       [0.5 0.98 0.46 ]^T
      //    X_sub =       [0.2 0.3  0.4 ; 
      //                   1.0 1.0  1.0  ]^T  (design matrix, last column = 1)
      //    targets_sub = [0.4 0.5  0.6  ]
      // 
      // Why all this trouble? Because the submatrices will often be much smaller than the full
      // ones, so they are much faster to invert (note the .inverse() call)
      
      // Get a vector where 1 represents that W_vec >= epsilon, and 0 otherswise
      VectorXi large_enough = (W_vec.array() >= epsilon).select(VectorXi::Ones(W_vec.size()), VectorXi::Zero(W_vec.size()));

      // Number of samples in the submatrices
      int n_samples_sub = large_enough.sum();
    
      // This would be a 1-liner in Matlab... but Eigen is not good with splicing.
      VectorXd W_vec_sub(n_samples_sub);
      MatrixXd X_sub(n_samples_sub,n_betas);
      MatrixXd targets_sub(n_samples_sub,targets.cols());
      int jj=0;
      for (int ii=0; ii<n_samples; ii++)
      {
        if (large_enough[ii]==1)
        {
          W_vec_sub[jj] = W_vec[ii];
          X_sub.row(jj) = X.row(ii);
          targets_sub.row(jj) = targets.row(ii);
          jj++;
        }
      }
      
      // Do the same inversion as above, but with only a small subset of the data
      MatrixXd W_sub = W_vec_sub.asDiagonal();
      VectorXd cur_beta_sub = (X_sub.transpose()*W_sub*X_sub).inverse()*X_sub.transpose()*W_sub*targets_sub;
   
      //cout << "  n_samples=" << n_samples << endl;
      //cout << "  n_samples_sub=" << n_samples_sub << endl;
      //cout << cur_beta.transpose() << endl;
      //cout << cur_beta_sub.transpose() << endl;
      beta.row(bb)   =    cur_beta_sub;
    }
  }
  MatrixXd offsets = beta.rightCols(1);
  MatrixXd slopes = beta.leftCols(n_betas-1);
  
  setModelParameters(new ModelParametersLWR(centers,widths,slopes,offsets));
  
}

void FunctionApproximatorLWR::predict(const MatrixXd& inputs, MatrixXd& output)
{
  if (!isTrained())  
  {
    cerr << "WARNING: You may not call FunctionApproximatorLWPR::predict if you have not trained yet. Doing nothing." << endl;
    return;
  }

  // No cast    : 8.90 microseconds/prediction of 1 input sample
  // Static cast: 8.91 microseconds/prediction of 1 input sample
  const ModelParametersLWR* model_parameters_lwr = static_cast<const ModelParametersLWR*>(getModelParameters());
  
  model_parameters_lwr->locallyWeightedLines(inputs, output);
}



