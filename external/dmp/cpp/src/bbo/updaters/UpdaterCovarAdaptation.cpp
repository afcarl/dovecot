#include "bbo/updaters/UpdaterCovarAdaptation.h"

#include <iomanip>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

UpdaterCovarAdaptation::UpdaterCovarAdaptation(double eliteness, string weighting_method, const VectorXd& base_level, bool diag_only, double learning_rate)
: UpdaterMean(eliteness, weighting_method), 
  diag_only_(diag_only),
  learning_rate_(learning_rate),
  base_level_as_diagonal_matrix_(base_level.asDiagonal())
{
  assert(learning_rate_>=0.0 && learning_rate_<=1.0);
}

void UpdaterCovarAdaptation::updateDistribution(const DistributionGaussian& distribution, const MatrixXd& samples, const VectorXd& costs, VectorXd& weights, DistributionGaussian& distribution_new) const
{
  int n_samples = samples.rows();
  int n_dims = samples.cols();
  
  VectorXd mean_cur = distribution.mean();
  assert(mean_cur.size()==n_dims);
  assert(costs.size()==n_samples);
  
  // Update the mean
  VectorXd mean_new;
  updateDistributionMean(mean_cur, samples, costs, weights, mean_new); 
  distribution_new.set_mean(mean_new);

  
  
  // Update the covariance matrix with reward-weighted averaging
  MatrixXd eps = samples - mean_cur.transpose().replicate(n_samples,1);
  // In Matlab: covar_new = (repmat(weights,1,n_dims).*eps)'*eps;
  MatrixXd weighted_eps = weights.replicate(1,n_dims).array()*eps.array();
  MatrixXd covar_new = weighted_eps.transpose()*eps;

  //MatrixXd summary(n_samples,2*n_dims+2);
  //summary << samples, eps, costs, weights;
  //cout << fixed << setprecision(2);
  //cout << summary << endl;

  // Remove non-diagonal values
  if (diag_only_) {
    MatrixXd diagonalized = covar_new.diagonal().asDiagonal();
    covar_new = diagonalized;    
  }
  
  // Low-pass filter for covariance matrix, i.e. weight between current and new covariance matrix.
  if (learning_rate_<1.0) {
    MatrixXd covar_cur = distribution.covar();
    covar_new = (1-learning_rate_)*covar_cur + learning_rate_*covar_new;
  }
  
  // Add a base_level to avoid pre-mature convergence
  if (base_level_as_diagonal_matrix_.rows()>0) // If base_level is empty, do nothing
  {
    assert(base_level_as_diagonal_matrix_.rows()==n_dims);
    covar_new = covar_new + base_level_as_diagonal_matrix_;
  }
  
  distribution_new.set_covar(covar_new);

  
}
