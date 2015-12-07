/**
 * @file   ModelParametersGMR.h
 * @brief  ModelParametersGMR class source file.
 * @author Thibaut Munzer, Freek Stulp
 */
 
#include "functionapproximators/ModelParametersGMR.h"

#include "utilities/ParseJSON.hpp"
#include "utilities/EigenJSON.hpp"
#include <boost/regex.hpp>

#include <limits>
#include <iostream>

using namespace Eigen;
using namespace std;

ModelParametersGMR::ModelParametersGMR(std::vector<VectorXd*> centers, std::vector<double*> priors,
    std::vector<MatrixXd*> slopes, std::vector<VectorXd*> biases,
    std::vector<MatrixXd*> inverseCovarsL)
:
  centers_(centers),
  priors_(priors),
  slopes_(slopes),
  biases_(biases),
  inverseCovarsL_(inverseCovarsL)
{  
  size_t nb_receptive_fields = centers.size();
  assert(priors.size() == nb_receptive_fields);
  assert(slopes.size() == nb_receptive_fields);
  assert(biases.size() == nb_receptive_fields);
  assert(inverseCovarsL.size() == nb_receptive_fields);

  nb_in_dim_ = centers[0]->size();
  for (size_t i = 0; i < nb_receptive_fields; i++)
  {
    assert(centers[i]->size() == nb_in_dim_);
    assert(slopes[i]->cols() == nb_in_dim_);
    assert(inverseCovarsL[i]->rows() == nb_in_dim_);
    assert(inverseCovarsL[i]->cols() == nb_in_dim_);
  }

  int nb_out_dim = slopes[0]->rows();
  for (size_t i = 0; i < nb_receptive_fields; i++)
  {
    assert(slopes[i]->rows() == nb_out_dim);
    assert(biases[i]->size() == nb_out_dim);
  }
  
  all_values_vector_size_ = 0;
  
  all_values_vector_size_ += centers_.size() * centers_[0]->size();
  all_values_vector_size_ += priors_.size();
  all_values_vector_size_ += slopes_.size() * slopes_[0]->rows() * slopes_[0]->cols();
  all_values_vector_size_ += biases_.size() * biases_[0]->size();
  all_values_vector_size_ += inverseCovarsL_.size() * (inverseCovarsL_[0]->rows() * (inverseCovarsL_[0]->cols() + 1)) / 2;
  
};

ModelParameters* ModelParametersGMR::clone(void) const
{
  std::vector<VectorXd*> centers;
  for (size_t i = 0; i < centers_.size(); i++)
    centers.push_back(new VectorXd(*(centers_[i])));

  std::vector<double*> priors;
  for (size_t i = 0; i < priors_.size(); i++)
    priors.push_back(new double(*(priors_[i])));

  std::vector<MatrixXd*> slopes;
  for (size_t i = 0; i < slopes_.size(); i++)
    slopes.push_back(new MatrixXd(*(slopes_[i])));

  std::vector<VectorXd*> biases;
  for (size_t i = 0; i < biases_.size(); i++)
    biases.push_back(new VectorXd(*(biases_[i])));

  std::vector<MatrixXd*> inverseCovarsL;
  for (size_t i = 0; i < inverseCovarsL_.size(); i++)
    inverseCovarsL.push_back(new MatrixXd(*(inverseCovarsL_[i])));

  return new ModelParametersGMR(centers, priors, slopes, biases, inverseCovarsL); 
}

int ModelParametersGMR::getExpectedInputDim(void) const  {
  return nb_in_dim_;
};

ostream& ModelParametersGMR::serialize(ostream& output) const {
  output << "{ \"ModelParametersGMR\": {";

  // Check if there are receptive fields.
  if (centers_.size() > 0)
  {
    output << "\"centers\": ";
    output << serializeJSON(centers_);

    output << ", \"priors\": ";
    output << "[ ";
    for (size_t i=0; i<priors_.size(); i++)
    {
      if (i>0) output << ",";
      output << *(priors_[i]) << " ";
    }
    output << "]";

    output << ", \"slopes\": ";
    output << serializeJSON(slopes_);

    output << ", \"biases\": ";
    output << serializeJSON(biases_);

    output << ", \"inverse_covars_l\": ";
    output << serializeJSON(inverseCovarsL_);
  }

  output  << " } }";                          
  return output;
};


// nnn Ask Thibaut about simplifying this
ModelParametersGMR* ModelParametersGMR::deserialize(istream& input_stream)
{

  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);
  
  if (json_string.empty())
    return NULL;
    
  vector<VectorXd> centers;
  RowVectorXd priors_matrix;
  vector<MatrixXd> slopes;
  vector<VectorXd> biases;
  vector<MatrixXd> inverse_covars_l;
  
  deserializeStdVectorEigenVectorJSON(getJSONValue(json_string,"centers"),centers);
  deserializeRowVectorJSON           (getJSONValue(json_string,"priors"),priors_matrix);
  deserializeStdVectorEigenMatrixJSON(getJSONValue(json_string,"slopes"),slopes);
  deserializeStdVectorEigenVectorJSON(getJSONValue(json_string,"biases"),biases);
  deserializeStdVectorEigenMatrixJSON(getJSONValue(json_string,"inverse_covars_l"),inverse_covars_l);
  
  unsigned int size = centers.size();
  vector<double*>   priors_p(size);
  vector<VectorXd*> centers_p(size);
  vector<MatrixXd*> slopes_p(size);
  vector<VectorXd*> biases_p(size);
  vector<MatrixXd*> inverse_covars_l_p(size);
  for (size_t ii=0; ii<centers.size(); ii++)
  {
    centers_p[ii] = &(centers[ii]);
    priors_p[ii] = &(priors_matrix[ii]);
    slopes_p[ii] = &(slopes[ii]);
    biases_p[ii] = &(biases[ii]);
    inverse_covars_l_p[ii] = &(inverse_covars_l[ii]);
  }
  
  return new ModelParametersGMR(centers_p,priors_p,slopes_p,biases_p,inverse_covars_l_p);
}

void ModelParametersGMR::getSelectableParameters(set<string>& selected_values_labels) const 
{
  selected_values_labels = set<string>();
  selected_values_labels.insert("centers");
  selected_values_labels.insert("priors");
  selected_values_labels.insert("slopes");
  selected_values_labels.insert("biases");
  selected_values_labels.insert("inverse_covars_l");
}

void ModelParametersGMR::getParameterVectorMask(const std::set<std::string> selected_values_labels, VectorXi& selected_mask) const
{

  selected_mask.resize(getParameterVectorAllSize());
  selected_mask.fill(0);
  
  int offset = 0;
  int size;

  size = centers_.size() * centers_[0]->size();
  if (selected_values_labels.find("centers")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(1);
  offset += size;
  
  size = priors_.size();
  if (selected_values_labels.find("priors")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(2);
  offset += size;

  size = slopes_.size() * slopes_[0]->rows() * slopes_[0]->cols();
  if (selected_values_labels.find("slopes")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(3);
  offset += size;

    
  size = biases_.size() * biases_[0]->size();
  if (selected_values_labels.find("biases")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(4);
  offset += size;

  size = inverseCovarsL_.size() * (inverseCovarsL_[0]->rows() * (inverseCovarsL_[0]->cols() + 1))/2;
  if (selected_values_labels.find("inverse_covars_l")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(5);
  offset += size;
    
  assert(offset == getParameterVectorAllSize());   
}


void ModelParametersGMR::getParameterVectorAll(VectorXd& values) const
{
  values.resize(getParameterVectorAllSize());
  int offset = 0;

  for (size_t i = 0; i < centers_.size(); i++)
  {
    values.segment(offset, centers_[i]->size()) = *(centers_[i]);
    offset += centers_[i]->size();
  }

  for (size_t i = 0; i < centers_.size(); i++)
  {
    values[offset] = *(priors_[i]);
    offset += 1;
  }

  for (size_t i = 0; i < slopes_.size(); i++)
  {
    for (int col = 0; col < slopes_[i]->cols(); col++)
    {
      values.segment(offset, slopes_[i]->rows()) = slopes_[i]->col(col);
      offset += slopes_[i]->rows();
    }
  }

  for (size_t i = 0; i < centers_.size(); i++)
  {
    values.segment(offset, biases_[i]->size()) = *(biases_[i]);
    offset += biases_[i]->size();
  }

  for (size_t i = 0; i < inverseCovarsL_.size(); i++)
  {
    for (int row = 0; row < inverseCovarsL_[i]->rows(); row++)
      for (int col = 0; col < row + 1; col++)
      {
        values[offset] = (*inverseCovarsL_[i])(row, col);
        offset += 1;
      }
  }
  
  assert(offset == getParameterVectorAllSize());   

};

void ModelParametersGMR::setParameterVectorAll(const VectorXd& values)
{
  if (all_values_vector_size_ != values.size())
  {
    cerr << __FILE__ << ":" << __LINE__ << ": values is of wrong size." << endl;
    return;
  }
  
  int offset = 0;

  for (size_t i = 0; i < centers_.size(); i++)
  {
    *(centers_[i]) = values.segment(offset, centers_[i]->size());
    offset += centers_[i]->size();
  }
  for (size_t i = 0; i < centers_.size(); i++)
  {
    *(priors_[i]) = values[offset];
    offset += 1;
  }

  for (size_t i = 0; i < slopes_.size(); i++)
  {
    for (int col = 0; col < slopes_[i]->cols(); col++)
    {
      slopes_[i]->col(col) = values.segment(offset, slopes_[i]->rows());
      offset += slopes_[i]->rows();
    }
  }

  for (size_t i = 0; i < centers_.size(); i++)
  {
    *(biases_[i]) = values.segment(offset, biases_[i]->size());
    offset += biases_[i]->size();
  }

  for (size_t i = 0; i < inverseCovarsL_.size(); i++)
  {
    for (int row = 0; row < inverseCovarsL_[i]->rows(); row++)
      for (int col = 0; col < row + 1; col++)
      {
        (*inverseCovarsL_[i])(row, col) = values[offset];
        offset += 1;
      }
  }
  
  assert(offset == getParameterVectorAllSize());

};
