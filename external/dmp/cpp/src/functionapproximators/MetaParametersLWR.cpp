/**
 * @file   MetaParametersLWR.h
 * @brief  MetaParametersLWR class source file.
 * @author Freek Stulp
 */

#include "functionapproximators/MetaParametersLWR.h"
 
#include "utilities/EigenJSON.hpp"
#include "utilities/ParseJSON.hpp"

#include <iostream>
#include <boost/lexical_cast.hpp>
#include <unordered_map>


using namespace Eigen;
using namespace std;

MetaParametersLWR::MetaParametersLWR(int expected_input_dim, const vector<VectorXd>& centers_per_dim, double overlap)
:
  MetaParameters(expected_input_dim),
  n_bfs_per_dim_(VectorXi::Zero(0)),
  centers_per_dim_(centers_per_dim),
  overlap_(overlap)
{
  assert(expected_input_dim==(int)centers_per_dim_.size());
  for (unsigned int dd=0; dd<centers_per_dim_.size(); dd++)
    assert(centers_per_dim_[dd].size()>0);  
}
  
MetaParametersLWR::MetaParametersLWR(int expected_input_dim, const VectorXi& n_bfs_per_dim, double overlap) 
:
  MetaParameters(expected_input_dim),
  n_bfs_per_dim_(n_bfs_per_dim),
  centers_per_dim_(std::vector<Eigen::VectorXd>(0)),
  overlap_(overlap)
{
  assert(expected_input_dim==n_bfs_per_dim_.size());
  for (int dd=0; dd<n_bfs_per_dim_.size(); dd++)
    assert(n_bfs_per_dim_[dd]>0);
  assert(overlap_>0.0);
};

MetaParametersLWR::MetaParametersLWR(int expected_input_dim, int n_bfs, double overlap) 
:
  MetaParameters(expected_input_dim),
  n_bfs_per_dim_(VectorXi::Constant(1,n_bfs)),
  centers_per_dim_(std::vector<Eigen::VectorXd>(0)),
  overlap_(overlap)
{
  assert(expected_input_dim==n_bfs_per_dim_.size());
  for (int dd=0; dd<n_bfs_per_dim_.size(); dd++)
    assert(n_bfs_per_dim_[dd]>0);
  assert(overlap_>0.0);
};

MetaParametersLWR* MetaParametersLWR::clone(void) const
{
  MetaParametersLWR* cloned;
  if (centers_per_dim_.size()>0)
    cloned =  new MetaParametersLWR(getExpectedInputDim(),centers_per_dim_,overlap_);
  else
    cloned =  new MetaParametersLWR(getExpectedInputDim(),n_bfs_per_dim_,overlap_);
  
  return cloned;
}

ostream& MetaParametersLWR::serialize(ostream& output) const
{
  output << "{ \"MetaParametersLWR\": {";
  output << "\"expected_input_dim\": " << getExpectedInputDim() << ", ";
  output << "\"n_bfs_per_dim\":" << serializeJSON(n_bfs_per_dim_) << ", ";
  output << "\"centers_per_dim\": [";
  // zzz Move this to EigenJSON
  for (unsigned int dd=0; dd<centers_per_dim_.size(); dd++)
  {
    if (dd>0) output << ", ";
    output << serializeJSON(centers_per_dim_[dd]);
  }
  output << "], ";
  output << "\"overlap\":" << overlap_ << "";
  output << " } }";
  return output;  // for multiple << operators.
}

MetaParametersLWR* MetaParametersLWR::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);

  if (json_string.empty())
    return NULL;

  int expect_dim;
  double overlap;
  MatrixXi n_bfs_per_dim;
  vector<VectorXd> centers_per_dim;
  
  expect_dim = boost::lexical_cast<int>   (getJSONValue(json_string,"expected_input_dim"));
  overlap    = boost::lexical_cast<double>(getJSONValue(json_string,"overlap"));
  deserializeMatrixJSON                   (getJSONValue(json_string,"n_bfs_per_dim"),n_bfs_per_dim);
  if (n_bfs_per_dim.rows()>0)
  {
    return new MetaParametersLWR(expect_dim, n_bfs_per_dim, overlap);
  } 
  else
  {
    deserializeStdVectorEigenVectorJSON(getJSONValue(json_string,"centers_per_dim"),centers_per_dim);
    return new MetaParametersLWR(expect_dim, centers_per_dim, overlap);
  }
  
}


/** \todo Document this rather complex function */
void MetaParametersLWR::getCentersAndWidths(const VectorXd& min, const VectorXd& max, Eigen::MatrixXd& centers, Eigen::MatrixXd& widths) const
{
  int n_dims = getExpectedInputDim();
  assert(min.size()==n_dims);
  assert(max.size()==n_dims);
    
  vector<VectorXd> centers_per_dim_local(n_dims); 
  if (!centers_per_dim_.empty())
  {
    centers_per_dim_local = centers_per_dim_;
  }
  else
  {
    // Centers are not know yet, compute them based on min and max
    for (int i_dim=0; i_dim<n_dims; i_dim++)
      centers_per_dim_local[i_dim] = VectorXd::LinSpaced(n_bfs_per_dim_[i_dim],min[i_dim],max[i_dim]);
  }
  
  // Determine the widths from the centers (separately for each dimension)
  vector<VectorXd> widths_per_dim_local(n_dims); 
  for (int i_dim=0; i_dim<n_dims; i_dim++)
  {
    VectorXd cur_centers = centers_per_dim_local[i_dim]; // Abbreviation for convenience
    int n_centers = cur_centers.size();
    VectorXd cur_widths(n_centers);

    if (n_centers==1)
    {
      cur_widths[0] = 1.0;
    }
    else if (n_centers==2)
    {
      cur_widths.fill(sqrt(overlap_*(cur_centers[1]-cur_centers[0])));
    }
    else
    {
      cur_widths[0] = sqrt(overlap_*fabs(cur_centers[1]-cur_centers[0]));
      cur_widths[n_centers-1] = sqrt(overlap_*fabs(cur_centers[n_centers-1]-cur_centers[n_centers-2]));
      for (int cc=1; cc<n_centers-1; cc++)
      {
        double width_left  = sqrt(overlap_*fabs(cur_centers[cc-1]-cur_centers[cc]));
        double width_right = sqrt(overlap_*fabs(cur_centers[cc+1]-cur_centers[cc]));
        // Recommended width is the average of the recommended widths for left and right
        cur_widths[cc] = 0.5*(width_left+width_right);
      }
    }
    widths_per_dim_local[i_dim] = cur_widths;
  }

  VectorXd digit_max(n_dims);
  int n_centers = 1;
  for (int i_dim=0; i_dim<n_dims; i_dim++)
  {
    n_centers = n_centers*centers_per_dim_local[i_dim].size();
    digit_max[i_dim] = centers_per_dim_local[i_dim].size();
  }
  VectorXi digit = VectorXi::Zero(n_dims);
  
  centers.resize(n_centers,n_dims);
  widths.resize(n_centers,n_dims);
  int i_center=0;

  while (digit[0]<digit_max(0))
  {
    for (int i_dim=0; i_dim<n_dims; i_dim++)
    {
      centers(i_center,i_dim) = centers_per_dim_local[i_dim][digit[i_dim]];
      widths(i_center,i_dim) = widths_per_dim_local[i_dim][digit[i_dim]];
    }
    i_center++;
  
    // Increment last digit by one
    digit[n_dims-1]++;
    for (int i_dim=n_dims-1; i_dim>0; i_dim--)
    {
      if (digit[i_dim]>=digit_max[i_dim])
      {
        digit[i_dim] = 0;
        digit[i_dim-1]++;
      }
    }
  }
  
}

