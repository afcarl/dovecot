#include "bbo/updaters/UpdaterCovarDecay.h"

#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

UpdaterCovarDecay::UpdaterCovarDecay(double eliteness, double covar_decay_factor, string weighting_method)
: UpdaterMean(eliteness, weighting_method), 
  covar_decay_factor_(covar_decay_factor)
{
  
  // Do some checks here
  if (covar_decay_factor_<=0 || covar_decay_factor_>=1)
  {
    double default_covar_decay_factor = 0.95;
    cout << __FILE__ << ":" << __LINE__ << ":Covar decay must be in range <0-1>, but it is " << covar_decay_factor_ << ". Setting to default: " << default_covar_decay_factor << endl;
    covar_decay_factor_ = default_covar_decay_factor;
  }

}

void UpdaterCovarDecay::updateDistribution(const DistributionGaussian& distribution, const MatrixXd& samples, const VectorXd& costs, VectorXd& weights, DistributionGaussian& distribution_new) const
{
  // Update the mean
  VectorXd mean_new;
  updateDistributionMean(distribution.mean(), samples, costs, weights, mean_new); 
  distribution_new.set_mean(mean_new);
  
  // Update the covariance matrix
  distribution_new.set_covar(covar_decay_factor_*covar_decay_factor_*distribution.covar());
  
}
