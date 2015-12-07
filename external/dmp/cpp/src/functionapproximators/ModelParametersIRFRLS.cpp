/**
 * @file   ModelParametersIRFRLS.h
 * @brief  ModelParametersIRFRLS class source file.
 * @author Freek Stulp, Thibaut Munzer
 */
 
#include "functionapproximators/ModelParametersIRFRLS.h"

#include "utilities/ParseJSON.hpp"
#include "utilities/EigenJSON.hpp"
#include <boost/regex.hpp>

#include <iostream>

using namespace Eigen;
using namespace std;

ModelParametersIRFRLS::ModelParametersIRFRLS(MatrixXd linear_models, MatrixXd cosines_periodes, VectorXd cosines_phase)
:
  linear_models_(linear_models),
  cosines_periodes_(cosines_periodes),
  cosines_phase_(cosines_phase)
{
  int nb_cos = cosines_periodes.rows();
  assert(cosines_phase.size() == nb_cos);
  assert(linear_models.rows() == nb_cos);

  nb_in_dim_ = cosines_periodes.cols();
  // int nb_output_dim = linear_models.cols();
  
  all_values_vector_size_ = 0;
  all_values_vector_size_ += linear_models_.rows() * linear_models_.cols();
  all_values_vector_size_ += cosines_phase_.size();
  all_values_vector_size_ += cosines_periodes_.rows() * cosines_periodes_.cols();
};

ModelParameters* ModelParametersIRFRLS::clone(void) const {
  return new ModelParametersIRFRLS(linear_models_, cosines_periodes_, cosines_phase_); 
}

int ModelParametersIRFRLS::getExpectedInputDim(void) const  {
  return nb_in_dim_;
};

ostream& ModelParametersIRFRLS::serialize(ostream& output) const {
  output << "{ \"ModelParametersIRFRLS\": {";
  output << "\"linear_models\": " << serializeJSON(linear_models_) << ", ";
  output << "\"cosines_periodes\": "  << serializeJSON(cosines_periodes_) << ", ";
  output << "\"cosines_phase\": " << serializeJSON(cosines_phase_) << "";
  output  << " } }";                          
  return output;
};

ModelParametersIRFRLS* ModelParametersIRFRLS::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);

  if (json_string.empty())
    return NULL;
  
  MatrixXd linear_models, cosines_periodes, cosines_phase;
  
  deserializeMatrixJSON(getJSONValue(json_string,"linear_models"),linear_models);
  deserializeMatrixJSON(getJSONValue(json_string,"cosines_periodes"),cosines_periodes);
  deserializeMatrixJSON(getJSONValue(json_string,"cosines_phase"),cosines_phase);
  
  return new ModelParametersIRFRLS(linear_models,cosines_periodes,cosines_phase);

  return NULL;
}

void ModelParametersIRFRLS::getSelectableParameters(set<string>& selected_values_labels) const 
{
  selected_values_labels = set<string>();
  selected_values_labels.insert("linear_model");
  selected_values_labels.insert("phases");
  selected_values_labels.insert("periods");
}

void ModelParametersIRFRLS::getParameterVectorMask(const std::set<std::string> selected_values_labels, VectorXi& selected_mask) const
{
  selected_mask.resize(getParameterVectorAllSize());
  selected_mask.fill(0);
  
  int offset = 0;
  int size;
  
  size = linear_models_.rows() * linear_models_.cols();
  if (selected_values_labels.find("linear_model")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(1);
  offset += size;
  
  size =  cosines_phase_.size();
  if (selected_values_labels.find("phases")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(2);
  offset += size;
  
  size = cosines_periodes_.rows() * cosines_periodes_.cols();
  if (selected_values_labels.find("periods")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(3);
  offset += size;
  
  assert(offset == getParameterVectorAllSize()); 
}

void ModelParametersIRFRLS::getParameterVectorAll(VectorXd& values) const
{
  values.resize(getParameterVectorAllSize());
  int offset = 0;
  
  for (int c = 0; c < linear_models_.cols(); c++)
  {
    values.segment(offset, linear_models_.rows()) = linear_models_.col(c);
    offset += linear_models_.rows();
  }

  values.segment(offset, cosines_phase_.size()) = cosines_phase_;
  offset += cosines_phase_.size();

  for (int c = 0; c < cosines_periodes_.cols(); c++)
  {
    values.segment(offset, cosines_periodes_.rows()) = cosines_periodes_.col(c);
    offset += cosines_periodes_.rows();
  }

  assert(offset == getParameterVectorAllSize()); 
  
};

void ModelParametersIRFRLS::setParameterVectorAll(const VectorXd& values)
{
  if (all_values_vector_size_ != values.size())
  {
    cerr << __FILE__ << ":" << __LINE__ << ": values is of wrong size." << endl;
    return;
  }
  
  int offset = 0;
  for (int c = 0; c < linear_models_.cols(); c++)
  {
    linear_models_.col(c) = values.segment(offset, linear_models_.rows());
    offset += linear_models_.rows();
  }
  
  cosines_phase_ = values.segment(offset, cosines_phase_.size());
  offset += cosines_phase_.size();

  for (int c = 0; c < cosines_periodes_.cols(); c++)
  {
    cosines_periodes_.col(c) = values.segment(offset, cosines_periodes_.rows());
    offset += cosines_periodes_.rows();
  }

  assert(offset == getParameterVectorAllSize());   
};
