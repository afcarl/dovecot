/**
 * \file demoTrainFunctionApproximators.cpp
 * \author Freek Stulp
 * \brief  Demonstrates how to initialize and train a function approximator..
 *
 * \ingroup Demos
 * \ingroup FunctionApproximators
 */

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <time.h>
#include <boost/filesystem.hpp>

#include "functionapproximators/FunctionApproximatorGMR.h"
#include "functionapproximators/FunctionApproximatorIRFRLS.h"
#include "functionapproximators/FunctionApproximatorLWPR.h"
#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/MetaParametersGMR.h"
#include "functionapproximators/MetaParametersIRFRLS.h"
#include "functionapproximators/MetaParametersLWPR.h"
#include "functionapproximators/MetaParametersLWR.h"


#include "targetFunction.hpp"

using namespace std;
using namespace Eigen;

/** Compute mean absolute error for each column of two matrices.
 *  \param[in] mat1 First matrix of data 
 *  \param[in] mat2 Second matrix of data
 *  \return Mean absolute error between the matrices (one value for each column)
 */
VectorXd meanAbsoluteErrorPerOutputDimension(const MatrixXd& mat1, const MatrixXd& mat2)
{
  MatrixXd abs_error = (mat1.array()-mat2.array()).abs();
  VectorXd mean_abs_error_per_output_dim = abs_error.colwise().mean();
     
  cout << fixed << setprecision(5);
  cout << "         Mean absolute error ";
  if (mean_abs_error_per_output_dim.size()>1) cout << " (per dimension)";
  cout << ": " << mean_abs_error_per_output_dim.transpose();      
  cout << "   \t(range of target data is " << mat1.colwise().maxCoeff().array()-mat1.colwise().minCoeff().array() << ")";
  
  return mean_abs_error_per_output_dim;
}

/** Main function
 * \param[in] n_args Number of arguments
 * \param[in] args Arguments themselves
 * \return Success of exection. 0 if successful.
 */
int main(int n_args, char** args)
{
  // First argument may be optional directory to write data to
  string directory;
  if (n_args>1)
    directory = string(args[1]);
  bool overwrite = true;
  
  
  // Generate training data 
  int n_input_dims = 1;
  VectorXi n_samples_per_dim = VectorXi::Constant(1,25);
  if (n_input_dims==2) 
    n_samples_per_dim = VectorXi::Constant(2,25);
    
  MatrixXd inputs, targets, outputs;
  targetFunction(n_samples_per_dim,inputs,targets);
  
  
  
  // Locally Weighted Regression
  double overlap = 0.07;
  int n_rfs = 9;
  if (n_input_dims==2) n_rfs = 5;
  VectorXi num_rfs_per_dim = VectorXi::Constant(n_input_dims,n_rfs);
  MetaParametersLWR* meta_parameters_lwr = new MetaParametersLWR(n_input_dims,num_rfs_per_dim,overlap);
  FunctionApproximator* fa = new FunctionApproximatorLWR(meta_parameters_lwr);

  cout << "_____________________________________" << endl << fa->getName() << endl;
  cout << "    Training"  << endl;
  fa->train(inputs,targets,directory+"/"+fa->getName(),overwrite);
  cout << "    Predicting" << endl;
  fa->predict(inputs,outputs);
  meanAbsoluteErrorPerOutputDimension(targets,outputs);
  cout << endl << endl;
  
  delete fa;

  
  // IRFRLS
  int number_of_basis_functions=100;
  double lambda=0.2;
  double gamma=10;
  MetaParametersIRFRLS* meta_parameters_irfrls = new MetaParametersIRFRLS(n_input_dims,number_of_basis_functions,lambda,gamma);
  fa = new FunctionApproximatorIRFRLS(meta_parameters_irfrls);
  
  cout << "_____________________________________" << endl << fa->getName() << endl;
  cout << "    Training"  << endl;
  fa->train(inputs,targets,directory+"/"+fa->getName(),overwrite);
  cout << "    Predicting" << endl;
  fa->predict(inputs,outputs);
  meanAbsoluteErrorPerOutputDimension(targets,outputs);
  cout << endl << endl;
  
  delete fa;
  
  
  
  /*
  // Gaussian Mixture Regression  (TOO SLOW FOR DEMO)
  int number_of_gaussians = 5;
  MetaParametersGMR* meta_parameters_gmr = new MetaParametersGMR(n_input_dims,number_of_gaussians);
  fa = new FunctionApproximatorGMR(meta_parameters_gmr);
    
  cout << "_____________________________________" << endl << fa->getName() << endl;
  cout << "    Training"  << endl;
  fa->train(inputs,targets,directory+"/"+fa->getName(),overwrite);
  cout << "    Predicting" << endl;
  fa->predict(inputs,outputs);
  meanAbsoluteErrorPerOutputDimension(targets,outputs);
  cout << endl << endl;
  
  delete fa;


  
    // Locally Weighted Projection Regression  (LIBRARIES NOT LINKED CORRECTLY IN PYTHON)
#ifdef USE_LWPR
  double   w_gen=0.2;
  double   w_prune=0.8;
  bool     update_D=true;
  double   init_alpha=0.1;
  double   penalty=0.1;
  VectorXd init_D=VectorXd::Constant(n_input_dims,20);
  MetaParametersLWPR* meta_parameters_lwpr = new MetaParametersLWPR(n_input_dims,init_D,w_gen,w_prune,update_D,init_alpha,penalty);
  fa = new FunctionApproximatorLWPR(meta_parameters_lwpr);
    
  cout << "_____________________________________" << endl << fa->getName() << endl;
  cout << "    Training"  << endl;
  fa->train(inputs,targets,directory+"/"+fa->getName(),overwrite);
  cout << "    Predicting" << endl;
  fa->predict(inputs,outputs);
  meanAbsoluteErrorPerOutputDimension(targets,outputs);
  cout << endl << endl;
  
  delete fa;
#endif // USE_LWPR

  */
 
  return 0;
}


