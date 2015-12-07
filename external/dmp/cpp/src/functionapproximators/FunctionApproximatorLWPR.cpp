/**
 * @file   FunctionApproximatorLWPR.cpp
 * @brief  FunctionApproximator class source file.
 * @author Thibaut Munzer, Freek Stulp
 */
 
/*
 * Copyright (C) 2013 MACSi Project
 * author:  Thibaut Munzer, Freek Stulp
 * website: www.macsi.isir.upmc.fr
 *
 * Permission is granted to copy, distribute, and/or modify this program
 * under the terms of the GNU General Public License, version 2 or any
 * later version published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
 * Public License for more details
 */
 
#include "functionapproximators/FunctionApproximatorLWPR.h"

#include "functionapproximators/MetaParametersLWPR.h"
#include "functionapproximators/ModelParametersLWPR.h"

#include "lwpr.hh"

#include <iostream>

using namespace Eigen;
using namespace std;

FunctionApproximatorLWPR::FunctionApproximatorLWPR(MetaParametersLWPR *meta_parameters, ModelParametersLWPR *model_parameters) 
:
  FunctionApproximator(meta_parameters,model_parameters)
{
}

FunctionApproximatorLWPR::FunctionApproximatorLWPR(ModelParametersLWPR *model_parameters) 
:
  FunctionApproximator(model_parameters)
{
}

FunctionApproximator* FunctionApproximatorLWPR::clone(void) const {
  MetaParametersLWPR*  meta_params  = NULL;
  if (getMetaParameters()!=NULL)
    meta_params = dynamic_cast<MetaParametersLWPR*>(getMetaParameters()->clone());

  ModelParametersLWPR* model_params = NULL;
  if (getModelParameters()!=NULL)
    model_params = dynamic_cast<ModelParametersLWPR*>(getModelParameters()->clone());

  if (meta_params==NULL)
    return new FunctionApproximatorLWPR(model_params);
  else
    return new FunctionApproximatorLWPR(meta_params,model_params);
};

void FunctionApproximatorLWPR::train(const MatrixXd& inputs, const MatrixXd& targets)
{
  if (isTrained())  
  {
    cerr << "WARNING: You may not call FunctionApproximatorLWPR::train more than once. Doing nothing." << endl;
    cerr << "   (if you really want to retrain, call reTrain function instead)" << endl;
    return;
  }
  
  assert(inputs.rows() == targets.rows()); // Must have same number of examples
  assert(inputs.cols()==getExpectedInputDim());
  
  const MetaParametersLWPR* meta_parameters_lwpr = dynamic_cast<const MetaParametersLWPR*>(getMetaParameters());
  
  int n_in =inputs.cols();
  int n_out=targets.cols();
 
  LWPR_Object* lwpr_object = new LWPR_Object(n_in, n_out);
	lwpr_object->setInitD(    meta_parameters_lwpr->init_D_[0]); // zzz Fix this
	lwpr_object->wGen(        meta_parameters_lwpr->w_gen_);
  lwpr_object->wPrune(      meta_parameters_lwpr->w_prune_);
  lwpr_object->updateD(     meta_parameters_lwpr->update_D_);
  lwpr_object->setInitAlpha(meta_parameters_lwpr->init_alpha_);
  lwpr_object->penalty(     meta_parameters_lwpr->penalty_);
	lwpr_object->diagOnly(    meta_parameters_lwpr->diag_only_);
  lwpr_object->useMeta(     meta_parameters_lwpr->use_meta_);
  lwpr_object->metaRate(    meta_parameters_lwpr->meta_rate_);
  lwpr_object->kernel(      meta_parameters_lwpr->kernel_name_.c_str());
   
  
  vector<double> input_vector(n_in);
  vector<double> target_vector(n_out);
  int n_input_samples = inputs.rows();
  
  //http://stackoverflow.com/questions/15858569/randomly-permute-rows-columns-of-a-matrix-with-eigen
  PermutationMatrix<Dynamic,Dynamic> permute(n_input_samples);	
  permute.setIdentity();
  VectorXi shuffled_indices = VectorXi::LinSpaced(n_input_samples,0,n_input_samples-1);
  for (int iterations=0; iterations<2; iterations++)
  {
    random_shuffle(permute.indices().data(), permute.indices().data()+permute.indices().size());
    shuffled_indices = (shuffled_indices.transpose()*permute).transpose();

    for (int ii=0; ii<n_input_samples; ii++)
    {
      // Eigen::VectorXd -> std::vector
      Map<VectorXd>(input_vector.data(),n_in) = inputs.row(shuffled_indices[ii]);  
      Map<VectorXd>(target_vector.data(),n_out) = targets.row(shuffled_indices[ii]);
      // update model
      lwpr_object->update(input_vector, target_vector);
    }
  }
  
  setModelParameters(new ModelParametersLWPR(lwpr_object));
}


void FunctionApproximatorLWPR::predict(const MatrixXd& inputs, MatrixXd& outputs)
{
  if (!isTrained())  
  {
    cerr << "WARNING: You may not call FunctionApproximatorLWPR::predict if you have not trained yet. Doing nothing." << endl;
    return;
  }

  const ModelParametersLWPR* model_parameters_lwpr = static_cast<const ModelParametersLWPR*>(getModelParameters());

  int n_in  = model_parameters_lwpr->lwpr_object_->model.nIn;
  assert(inputs.cols()==n_in);
  
  int n_input_samples = inputs.rows();
  int n_out = model_parameters_lwpr->lwpr_object_->model.nOut;

  outputs.resize(n_input_samples,n_out);
  
  // Allocate memory for the temporary vectors for LWPR_Object::predict
  vector<double> input_vector(n_in);
  vector<double> output_vector(n_out);

  // Do prediction for each sample  
  for (int ii=0; ii<n_input_samples; ii++)
  {
    // LWPR_Object::predict uses std::vector, so do some conversions here.
    Map<VectorXd>(input_vector.data(),n_in) = inputs.row(ii);  // Eigen::VectorXd -> std::vector
    output_vector = model_parameters_lwpr->lwpr_object_->predict(input_vector);
    outputs.row(ii) = Map<VectorXd>(&output_vector[0], n_out); // std::vector -> Eigen::VectorXd
  }
  
}

