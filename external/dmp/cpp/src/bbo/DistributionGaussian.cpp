#include "bbo/DistributionGaussian.h"

#include <boost/random.hpp>
#include <boost/random/variate_generator.hpp>
#include <boost/random/normal_distribution.hpp>
#include <iomanip>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

boost::mt19937 DistributionGaussian::rng = boost::mt19937(getpid() + time(0));

DistributionGaussian::DistributionGaussian(const VectorXd& mean, const MatrixXd& covar) 
{
  mean_ = mean;
  set_covar(covar);
}

DistributionGaussian* DistributionGaussian::clone(void) const
{
  return new DistributionGaussian(mean(),covar()); 
}

void DistributionGaussian::set_mean(const VectorXd& mean) { 
  assert(mean.size()==mean_.size());  
  mean_ = mean;
}


void DistributionGaussian::set_covar(const MatrixXd& covar) { 
  assert(covar.cols()==covar.rows());
  assert(covar.rows()==mean_.size());

  covar_ = covar;
  
  // Now perform the Cholesky decomposition, which makes it easier to generate samples. 
  // Also see DistributionGaussian::generateSamples
  MatrixXd A(covar_.llt().matrixL());
  covar_decomposed_ = A;
  

}

void DistributionGaussian::generateSamples(int n_samples, MatrixXd& samples)
{
  int n_dims = mean_.size();
  samples.resize(n_samples,n_dims);
  
  // http://en.wikipedia.org/wiki/Multivariate_normal_distribution#Drawing_values_from_the_distribution
  boost::normal_distribution<> normal(0, 1);
  boost::variate_generator<boost::mt19937&, boost::normal_distribution<> > genZ(rng, normal);
  VectorXd z(n_dims);
  for (int i_sample=0; i_sample<n_samples; i_sample++)
  {
    // Generate vector with samples from standard normal distribution N(0,1) 
    for (int i_dim=0; i_dim<n_dims; i_dim++)
      z(i_dim) = genZ();

    // Compute x = mu + Az
    samples.row(i_sample) = mean_ + covar_decomposed_*z;
  }  
}

std::ostream& DistributionGaussian::serialize(std::ostream& output) const
{
  MatrixXd C = covar();
  MatrixXd C_only_diag = C.diagonal().asDiagonal();
  bool is_diag = (C.array()==C_only_diag.array()).all();
  if (is_diag)
    C = C_only_diag.diagonal().transpose();
  
  // zzz JSON
  output << "DistributionGaussian{mean=[" << mean().transpose() << "], covar=[";
  for (int dd=0; dd<C.rows(); dd++)
  {
    output << C.row(dd);
    if (dd<covar().rows()-1) output << ";  ";
  }
  output << "]}";
  return output;
}  

