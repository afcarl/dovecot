/**
 * @file   ModelParametersLWR.h
 * @brief  ModelParametersLWR class source file.
 * @author Freek Stulp
 */
 
#include "functionapproximators/ModelParametersLWR.h"

#include "utilities/ParseJSON.hpp"
#include "utilities/EigenJSON.hpp"
#include "utilities/EigenFileIO.hpp"

#include <iostream>
#include <fstream>

#include <eigen3/Eigen/Core>


using namespace std;
using namespace Eigen;


ModelParametersLWR::ModelParametersLWR(const MatrixXd& centers, const MatrixXd& widths, const MatrixXd& slopes, const MatrixXd& offsets) 
:
  centers_(centers),
  widths_(widths),
  slopes_(slopes), 
  offsets_(offsets),
  lines_pivot_at_max_activation_(false),
  slopes_as_angles_(false),
  caching_(true)
{
  int n_basis_functions = centers.rows();
  int n_dims = centers.cols();
  
  assert(n_basis_functions==widths_.rows());
  assert(n_dims           ==widths_.cols());
  assert(n_basis_functions==slopes_.rows());
  assert(n_dims           ==slopes_.cols());
  assert(n_basis_functions==offsets_.rows());
  assert(1                ==offsets_.cols());
  
  all_values_vector_size_ = 0;
  all_values_vector_size_ += centers_.rows()*centers_.cols();
  all_values_vector_size_ += widths_.rows() *widths_.cols();
  all_values_vector_size_ += offsets_.rows()*offsets_.cols();
  all_values_vector_size_ += slopes_.rows() *slopes_.cols();
  
};

ModelParameters* ModelParametersLWR::clone(void) const {
  return new ModelParametersLWR(centers_,widths_,slopes_,offsets_); 
}

void ModelParametersLWR::normalizedKernelActivations(const MatrixXd& inputs, MatrixXd& normalized_kernel_activations) const
{
  if (caching_)
  {
    // If the cached inputs matrix has the same size as the one now requested
    //     (this also takes care of the case when inputs_cached is empty and need to be initialized)
    if ( inputs.rows()==inputs_cached_.rows() && inputs.cols()==inputs_cached_.cols() )
    {
      // And they have the same values
      if ( (inputs.array()==inputs_cached_.array()).all() )
      {
        // Then you can return the cached values
        normalized_kernel_activations = normalized_kernel_activations_cached_;
        return;
      }
    }
  }

  // Cache could not be used, actually do the work
  normalizedKernelActivations(centers_,widths_,inputs,normalized_kernel_activations);

  if (caching_)
  {
    // Cache the current results now.  
    inputs_cached_ = inputs;
    normalized_kernel_activations_cached_ = normalized_kernel_activations;
  }
  
}

void ModelParametersLWR::set_lines_pivot_at_max_activation(bool lines_pivot_at_max_activation)
{
  // If no change, just return
  if (lines_pivot_at_max_activation_ == lines_pivot_at_max_activation)
    return;

  //cout << "________________" << endl;
  //cout << centers_.transpose() << endl;  
  //cout << slopes_.transpose() << endl;  
  //cout << offsets_.transpose() << endl;  
  //cout << "centers_ = " << centers_.rows() << "X" << centers_.cols() << endl;
  //cout << "slopes_ = " << slopes_.rows() << "X" << slopes_.cols() << endl;
  //cout << "offsets_ = " << offsets_.rows() << "X" << offsets_.cols() << endl;

  // If you pivot lines around the point when the basis function has maximum activation (i.e.
  // at the center of the Gaussian), you must compute the new offset corresponding to this
  // slope, and vice versa    
  int n_lines = centers_.rows();
  VectorXd ac(n_lines); // slopes*centers
  for (int i_line=0; i_line<n_lines; i_line++)
  {
    ac[i_line] = slopes_.row(i_line) * centers_.row(i_line).transpose();
  }
    
  if (lines_pivot_at_max_activation)
  {
    // Representation was "y = ax + b", now it will be "y = a(x-c) + b^new" 
    // Since "y = ax + b" can be rewritten as "y = a(x-c) + (b+ac)", we know that "b^new = (ac+b)"
    offsets_ = offsets_ + ac;
  }
  else
  {
    // Representation was "y = a(x-c) + b", now it will be "y = ax + b^new" 
    // Since "y = a(x-c) + b" can be rewritten as "y = ax + (b-ac)", we know that "b^new = (b-ac)"
    offsets_ = offsets_ - ac;
  } 
  // Remark, the above could have been done as a one-liner, but I prefer the more legible version.
  
  //cout << offsets_.transpose() << endl;  
  //cout << "offsets_ = " << offsets_.rows() << "X" << offsets_.cols() << endl;
  
  lines_pivot_at_max_activation_ = lines_pivot_at_max_activation;
}

void ModelParametersLWR::set_slopes_as_angles(bool slopes_as_angles)
{

  slopes_as_angles_ = slopes_as_angles;
  cerr << __FILE__ << ":" << __LINE__ << ":";
  cerr << "Not implemented yet!!!" << endl;
  slopes_as_angles_ = false; // nnn Make sure it is turned off until it works ;-)
}




void ModelParametersLWR::getLines(const MatrixXd& inputs, MatrixXd& lines) const
{
  int n_time_steps = inputs.rows();

  //cout << "centers_ = " << centers_.rows() << "X" << centers_.cols() << endl;
  //cout << "slopes_ = " << slopes_.rows() << "X" << slopes_.cols() << endl;
  //cout << "offsets_ = " << offsets_.rows() << "X" << offsets_.cols() << endl;
  //cout << "inputs = " << inputs.rows() << "X" << inputs.cols() << endl;
  
  // Compute values along lines for each time step  
  // Line representation is "y = ax + b"
  lines = inputs*slopes_.transpose() + offsets_.transpose().replicate(n_time_steps,1);
  
  if (lines_pivot_at_max_activation_)
  {
    // Line representation is "y = a(x-c) + b", which is  "y = ax - ac + b"
    // Therefore, we still have to subtract "ac"
    int n_lines = centers_.rows();
    VectorXd ac(n_lines); // slopes*centers  = ac
    for (int i_line=0; i_line<n_lines; i_line++)
      ac[i_line] = slopes_.row(i_line) * centers_.row(i_line).transpose();
    //cout << "ac = " << ac.rows() << "X" << ac.cols() << endl;
    lines = lines - ac.transpose().replicate(n_time_steps,1);
  }
  //cout << "lines = " << lines.rows() << "X" << lines.cols() << endl;
}
  
void ModelParametersLWR::locallyWeightedLines(const MatrixXd& inputs, MatrixXd& output) const
{
  
  MatrixXd lines;
  getLines(inputs, lines);

  // Weight the values for each line with the normalized basis function activations  
  MatrixXd activations;
  normalizedKernelActivations(inputs,activations);
  
  output = (lines.array()*activations.array()).rowwise().sum();
}

void ModelParametersLWR::kernelActivations(const VectorXd& center, const VectorXd& width, const MatrixXd& inputs, Ref<VectorXd> kernel_activations)
{
  // center      =         1 x n_dim
  // width       =         1 x n_dim
  // inputs      = n_samples x n_dim
  // activations = n_samples x     1
  int n_dims    = center.size();
  int n_samples = inputs.rows();
  
  assert(n_dims==width.size());
  assert(n_dims==inputs.cols());

  // Here, we compute the values of a (unnormalized) multi-variate Gaussian:
  //   activation = exp(-0.5*(x-mu)*Sigma^-1*(x-mu))
  // Because Sigma is diagonal in our case, this simplifies to
  //   activation = exp(\sum_d=1^D [-0.5*(x_d-mu_d)^2/Sigma_(d,d)]) 
  //              = \prod_d=1^D exp(-0.5*(x_d-mu_d)^2/Sigma_(d,d)) 
  // This last product is what we compute below incrementally
  
  kernel_activations.resize(n_samples);
  kernel_activations.fill(1.0);
  for (int i_dim=0; i_dim<n_dims; i_dim++)
    kernel_activations.array() *= exp(-0.5*pow(inputs.col(i_dim).array()-center[i_dim],2)/(width[i_dim]*width[i_dim])).array();
}

void ModelParametersLWR::normalizedKernelActivations(const MatrixXd& centers, const MatrixXd& widths, const MatrixXd& inputs, MatrixXd& normalized_kernel_activations)
{
  // centers     = n_basis_functions x n_dim
  // widths      = n_basis_functions x n_dim
  // inputs      = n_samples         x n_dim
  // activations = n_samples         x n_basis_functions
  int n_basis_functions = centers.rows();
  int n_dims            = centers.cols();
  int n_samples         = inputs.rows();
  
  // Check and set sizes
  assert( (n_basis_functions==widths.rows()) & (n_dims==widths.cols()) ); 
  assert( (n_samples==inputs.rows()        ) & (n_dims==inputs.cols()) ); 
  normalized_kernel_activations.resize(n_samples,n_basis_functions);  

  // Get activations of kernels
  for (int bb=0; bb<n_basis_functions; bb++)
    kernelActivations(centers.row(bb),widths.row(bb),inputs,normalized_kernel_activations.col(bb));
  
  // Compute sum for each row (each value in input_vector)
  MatrixXd sum_kernel_activations = normalized_kernel_activations.rowwise().sum(); // n_samples x 1

  // Normalize for each row (each value in input_vector)  
  normalized_kernel_activations = normalized_kernel_activations.array()/sum_kernel_activations.replicate(1,n_basis_functions).array();
}


ostream& ModelParametersLWR::serialize(ostream& output) const {
  output << "{ \"ModelParametersLWR\": {";
  output << "\"centers\": " << serializeJSON(centers_) << ", ";
  output << "\"widths\": "  << serializeJSON(widths_) << ", ";
  output << "\"slopes\": "  << serializeJSON(slopes_) << ", ";
  output << "\"offsets\": " << serializeJSON(offsets_) << "";
  output  << " } }";                          
  return output;  // for multiple << operators.
};


ModelParametersLWR* ModelParametersLWR::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);

  if (json_string.empty())
    return NULL;

  MatrixXd centers, widths, offsets, slopes;
  
  deserializeMatrixJSON(getJSONValue(json_string,"centers"),centers);
  deserializeMatrixJSON(getJSONValue(json_string,"widths"),widths);
  deserializeMatrixJSON(getJSONValue(json_string,"offsets"),offsets);
  deserializeMatrixJSON(getJSONValue(json_string,"slopes"),slopes);
  
  return new ModelParametersLWR(centers,widths,slopes,offsets);
}

void ModelParametersLWR::getSelectableParameters(set<string>& selected_values_labels) const 
{
  selected_values_labels = set<string>();
  selected_values_labels.insert("centers");
  selected_values_labels.insert("widths");
  selected_values_labels.insert("offsets");
  selected_values_labels.insert("slopes");
}


void ModelParametersLWR::getParameterVectorMask(const std::set<std::string> selected_values_labels, VectorXi& selected_mask) const
{

  selected_mask.resize(getParameterVectorAllSize());
  selected_mask.fill(0);
  
  int offset = 0;
  int size;
  
  // Centers
  size = centers_.rows()*centers_.cols();
  if (selected_values_labels.find("centers")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(1);
  offset += size;
  
  // Widths
  size = widths_.rows()*widths_.cols();
  if (selected_values_labels.find("widths")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(2);
  offset += size;
  
  // Offsets
  size = offsets_.rows()*offsets_.cols();
  if (selected_values_labels.find("offsets")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(3);
  offset += size;

  // Slopes
  size = slopes_.rows()*slopes_.cols();
  if (selected_values_labels.find("slopes")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(4);
  offset += size;

  assert(offset == getParameterVectorAllSize());   
}

void ModelParametersLWR::getParameterVectorAll(VectorXd& values) const
{
  values.resize(getParameterVectorAllSize());
  int offset = 0;
  
  for (int i_dim=0; i_dim<centers_.cols(); i_dim++)
  {
    values.segment(offset,centers_.rows()) = centers_.col(i_dim);
    offset += centers_.rows();
  }
  
  for (int i_dim=0; i_dim<widths_.cols(); i_dim++)
  {
    values.segment(offset,widths_.rows()) = widths_.col(i_dim);
    offset += widths_.rows();
  }
  
  values.segment(offset,offsets_.rows()) = offsets_;
  offset += offsets_.rows();
  
  VectorXd cur_slopes;
  for (int i_dim=0; i_dim<slopes_.cols(); i_dim++)
  {
    cur_slopes = slopes_.col(i_dim);
    if (slopes_as_angles_)
    {
      // cur_slopes is a slope, but the values vector expects the angle with the x-axis. Do the 
      // conversion here.
      for (int ii=0; ii<cur_slopes.size(); ii++)
        cur_slopes[ii] = atan2(cur_slopes[ii],1.0);
    }
    
    values.segment(offset,slopes_.rows()) = cur_slopes;
    offset += slopes_.rows();
  }
  
  assert(offset == getParameterVectorAllSize());   
};

void ModelParametersLWR::setParameterVectorAll(const VectorXd& values) {

  if (all_values_vector_size_ != values.size())
  {
    cerr << __FILE__ << ":" << __LINE__ << ": values is of wrong size." << endl;
    return;
  }
  
  int offset = 0;
  int size = centers_.rows();
  int n_dims = centers_.cols();
  for (int i_dim=0; i_dim<n_dims; i_dim++)
  {
    // If the centers change, the cache for normalizedKernelActivations() must be cleared,
    // because this function will return different values for different centers
    if ( !(centers_.col(i_dim).array() == values.segment(offset,size).array()).all() )
      clearCache();
    
    centers_.col(i_dim) = values.segment(offset,size);
    offset += size;
  }
  for (int i_dim=0; i_dim<n_dims; i_dim++)
  {
    // If the centers change, the cache for normalizedKernelActivations() must be cleared,
    // because this function will return different values for different centers
    if ( !(widths_.col(i_dim).array() == values.segment(offset,size).array()).all() )
      clearCache();
    
    widths_.col(i_dim) = values.segment(offset,size);
    offset += size;
  }

  offsets_ = values.segment(offset,size);
  offset += size;
  // Cache must not be cleared, because normalizedKernelActivations() returns the same values.

  MatrixXd old_slopes = slopes_;
  for (int i_dim=0; i_dim<n_dims; i_dim++)
  {
    slopes_.col(i_dim) = values.segment(offset,size);
    offset += size;
    // Cache must not be cleared, because normalizedKernelActivations() returns the same values.
  }

  assert(offset == getParameterVectorAllSize());   
};

bool ModelParametersLWR::saveGridData(const VectorXd& min, const VectorXd& max, const VectorXi& n_samples_per_dim, string save_directory, bool overwrite) const
{
  if (save_directory.empty())
    return true;
  
  //cout << "        Saving LWR model grid data to: " << save_directory << "." << endl;
  
  int n_dims = min.size();
  assert(n_dims==max.size());
  assert(n_dims==n_samples_per_dim.size());
  
  MatrixXd inputs;
  if (n_dims==1)
  {
    inputs  = VectorXd::LinSpaced(n_samples_per_dim[0], min[0], max[0]);
  }
  else if (n_dims==2)
  {
    int n_samples = n_samples_per_dim[0]*n_samples_per_dim[1];
    inputs = MatrixXd::Zero(n_samples, n_dims);
    VectorXd x1 = VectorXd::LinSpaced(n_samples_per_dim[0], min[0], max[0]);
    VectorXd x2 = VectorXd::LinSpaced(n_samples_per_dim[1], min[1], max[1]);
    for (int ii=0; ii<x1.size(); ii++)
    {
      for (int jj=0; jj<x2.size(); jj++)
      {
        inputs(ii*x2.size()+jj,0) = x1[ii];
        inputs(ii*x2.size()+jj,1) = x2[jj];
      }
    }
  }  
      
  MatrixXd lines;
  getLines(inputs, lines);
  
  MatrixXd weighted_lines;
  locallyWeightedLines(inputs, weighted_lines);
  
  MatrixXd activations;
  normalizedKernelActivations(inputs, activations);
    
  saveMatrix(save_directory,"n_samples_per_dim.txt",n_samples_per_dim,overwrite);
  saveMatrix(save_directory,"inputs_grid.txt",inputs,overwrite);
  saveMatrix(save_directory,"lines.txt",lines,overwrite);
  saveMatrix(save_directory,"weighted_lines.txt",weighted_lines,overwrite);
  saveMatrix(save_directory,"activations_normalized.txt",activations,overwrite);
  
  return true;
  
}

void ModelParametersLWR::setParameterVectorModifierPrivate(std::string modifier, bool new_value)
{
  if (modifier.compare("lines_pivot_at_max_activation")==0)
    set_lines_pivot_at_max_activation(new_value);
  
  if (modifier.compare("slopes_as_angles")==0)
    set_slopes_as_angles(new_value);
  
}

