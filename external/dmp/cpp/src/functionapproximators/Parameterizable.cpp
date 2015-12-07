#include "functionapproximators/Parameterizable.h"

#include <iostream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;
  
void Parameterizable::setSelectedParameters(const std::set<std::string>& selected_values_labels)
{
  getParameterVectorMask(selected_values_labels,selected_mask_);
}

int Parameterizable::getParameterVectorSelectedSize(void) const
{  
  int all_size = 0;
  for (int all_ii=0; all_ii<selected_mask_.size(); all_ii++)
    if (selected_mask_[all_ii]>0)
      all_size++;
    
  return all_size;
}

void Parameterizable::getParameterVectorSelected(Eigen::VectorXd& values, bool normalized) const
{
  Eigen::VectorXd all_values;
  getParameterVectorAll(all_values);
  
  values.resize(getParameterVectorSelectedSize());
  // We cannot do this with Block, because regions might not be contiguous
  int ii = 0;
  for (int all_ii=0; all_ii<selected_mask_.size(); all_ii++)
    if (selected_mask_[all_ii]>0)
      values[ii++] = all_values[all_ii];
    
  if (normalized)
  {
    VectorXd min_vec, max_vec;
    getParameterVectorSelectedMinMax(min_vec, max_vec);
    
    VectorXd range =  (max_vec.array()-min_vec.array());
    for (int ii=0; ii<values.size(); ii++)
    {
      if (range[ii]>0)
      {
        values[ii] = (values[ii]-min_vec[ii])/range[ii];
      }
      else
      {
        if (abs(max_vec[ii])>0)
          values[ii] = values[ii]/abs(2*max_vec[ii]);
      }
    }
    
  }
    
}


void Parameterizable::setParameterVectorSelected(const VectorXd& values_arg, bool normalized)
{
  // If the initial parameter vector is still empty, get it now, before changing its value.
  if (parameter_vector_all_initial_.size()==0)
    getParameterVectorAll(parameter_vector_all_initial_);

  VectorXd all_values;
  getParameterVectorAll(all_values);
  
  VectorXd values = values_arg;
  if (normalized)
  {
    VectorXd min_vec, max_vec, range;
    getParameterVectorSelectedMinMax(min_vec, max_vec);
    range =  (max_vec.array()-min_vec.array());
    for (int ii=0; ii<values.size(); ii++)
    {
      if (range[ii]>0)
      {
        values[ii] = values[ii]*range[ii] + min_vec[ii];
      }
      else
      {
        if (abs(max_vec[ii])>0)
          values[ii] = values[ii]*abs(2*max_vec[ii]);
      }
    }
  }
  
  // We cannot do this with Eigen::Block, because regions might not be contiguous
  int ii = 0;
  for (int all_ii=0; all_ii<selected_mask_.size(); all_ii++)
    if (selected_mask_[all_ii]>0)
      all_values[all_ii] = values[ii++];
    
  setParameterVectorAll(all_values);
  
}

void Parameterizable::getParameterVectorSelectedMinMax(Eigen::VectorXd& min_vec, Eigen::VectorXd& max_vec) const
{
  VectorXd all_min_vec, all_max_vec;
  getParameterVectorAllMinMax(all_min_vec, all_max_vec);
  
  min_vec.resize(getParameterVectorSelectedSize());
  max_vec.resize(getParameterVectorSelectedSize());
  
  // We cannot do this with Eigen::Block, because regions might not be contiguous
  int ii = 0;
  for (int all_ii=0; all_ii<selected_mask_.size(); all_ii++)
  {
    if (selected_mask_[all_ii]>0)
    {
      min_vec[ii] = all_min_vec[all_ii];
      max_vec[ii] = all_max_vec[all_ii];
      ii++;
    }
  }
  
}

void Parameterizable::getParameterVectorAllMinMax(Eigen::VectorXd& min_vec, Eigen::VectorXd& max_vec) const
{
  set<string> all_selected_values_labels;
  getSelectableParameters(all_selected_values_labels);
  
  VectorXi selected_mask;
  getParameterVectorMask(all_selected_values_labels, selected_mask);
  
  // If the initial parameter vector is still empty, get it now.
  if (parameter_vector_all_initial_.size()==0)
    getParameterVectorAll(parameter_vector_all_initial_);
  
  Eigen::VectorXd all_values = parameter_vector_all_initial_;
  
  // Example: 
  // selected_mask = [ 1   1   1   0   0   0   3   3   3   0   0   0  ] 
  // all_values    = [1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 1.0 2.0 3.0 ] 
  //
  // For all blocks in selected_mask, compute the min/max in all_values for that block.
  // In the example above
  //   block 1 : min = 1.0; max = 3.0;
  //   block 3 : min = 7.0; max = 9.0;
  //
  // Then min_vec and max_vec will be as follows:
  //   min_vec = [1.0 1.0 1.0 7.0 7.0 7.0]
  //   max_vec = [3.0 3.0 3.0 9.0 9.0 9.0]
  
  min_vec.resize(getParameterVectorAllSize());
  max_vec.resize(getParameterVectorAllSize());

  // We cannot do this with Eigen::Block, because regions might not be contiguous
  int n_blocks = selected_mask.maxCoeff();
  int i_vec = 0;
  for (int i_block=1; i_block<=n_blocks; i_block++)
  {
    if ((selected_mask.array() == i_block).any())
    {
      double min_this_block = all_values.maxCoeff();
      double max_this_block = all_values.minCoeff(); 
      
      for (int all_ii=0; all_ii<selected_mask.size(); all_ii++)
      {
        if (selected_mask[all_ii]==i_block)
        {
          min_this_block =(all_values[all_ii]<min_this_block ? all_values[all_ii] : min_this_block);
          max_this_block =(all_values[all_ii]>max_this_block ? all_values[all_ii] : max_this_block);
        }
      }
      
      for (int all_ii=0; all_ii<selected_mask.size(); all_ii++)
      {
        if (selected_mask[all_ii]==i_block)
        {
          min_vec[i_vec] = min_this_block;
          max_vec[i_vec] = max_this_block;
          i_vec++;
        }
      }
      
      //cout << "_________________" << endl;
      //cout << "  i_block=" << i_block << endl;
      //cout << "  min_this_block=" << min_this_block << endl;
      //cout << "  max_this_block=" << max_this_block << endl;
      //cout << min_vec.transpose() << endl;
      //cout << max_vec.transpose() << endl;
    }
    
  }
    
}


/*
void Parameterizable::getParameterVectorSelectedMinMax(Eigen::VectorXd& min_vec, Eigen::VectorXd& max_vec) const
{

  Eigen::VectorXd all_min_values, all_max_values;
  getParameterVectorAllMinMax(all_min_values,all_max_values);
  
  min_vec.resize(getParameterVectorSelectedSize());
  max_vec.resize(getParameterVectorSelectedSize());
  // We cannot do this with Block, because regions might not be contiguous
  int ii = 0;
  for (int all_ii=0; all_ii<selected_mask_.size(); all_ii++)
  {
    if (selected_mask_[all_ii]>0)
    {
      min_vec[ii] = all_min_values[all_ii];  
      max_vec[ii] = all_max_values[all_ii];  
      ii++;
    }
  }
}
*/

void Parameterizable::setParameterVectorModifier(std::string modifier, bool new_value)
{
  if (parameter_vector_all_initial_.size()>0)
  {
    cerr << __FILE__ << ":" << __LINE__ << ":";
    cerr << "Warning: you can only set a ParameterVectorModifier if the intial state has not yet been determined." << endl;
    return;
  }
  setParameterVectorModifierPrivate(modifier, new_value);
}

