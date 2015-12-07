/**
 * @file   Updater.h
 * @brief  Updater class header file.
 * @author Freek Stulp
 */
 

#ifndef UPDATER_H
#define UPDATER_H

#include <vector>
#include <eigen3/Eigen/Core>

#include "bbo/UpdateSummary.h"
#include "bbo/DistributionGaussian.h"

/** Interface for the distribution update step in evolution strategies.
 *
 * Evolution strategies implement the following loop:
\code
// distribution has been initialized above
for (int i_update=1; i_update<=n_updates; i_update++)
  // Sample from distribution
  samples = distribution->generateSamples(n_samples_per_update);
  // Perform rollouts for the samples and compute costs
  costs = cost_function_solver->evaluate(samples);
  // Update parameters
  distribution = updater->updateDistribution(distribution, samples, costs);
}
\endcode
 *
 * The last step (updating the distribution) is implemented by classes inheriting from this Updater
 * interface.
 */
class Updater
{
public:
  
  /** Update a distribution given the samples and costs of an epoch.
   * \param[in] distribution Current distribution
   * \param[in] samples The samples in the epoch (size: n_samples X n_dims)
   * \param[in] costs Costs of the samples (size: n_samples x 1)
   * \param[out] weights The weights computed from the costs
   * \param[out] distribution_new Updated distribution
   * \param[out] summary An object containing all relevant update information, for logging and debugging purposes.
   */
  inline void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, Eigen::VectorXd& weights, DistributionGaussian& distribution_new, UpdateSummary& summary) 
  {
    summary.distribution = distribution.clone();
    summary.samples = samples;
    summary.costs = costs;
    updateDistribution(distribution, samples, costs, weights, distribution_new);
    summary.weights = weights;
    summary.distribution_new = distribution_new.clone();
  }

  /** Update a distribution given the samples and costs of an epoch.
   * \param[in] distribution Current distribution
   * \param[in] samples The samples in the epoch (size: n_samples X n_dims)
   * \param[in] costs Costs of the samples (size: n_samples x 1)
   * \param[out] distribution_new Updated distribution
   */
  inline void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, DistributionGaussian& distribution_new) {
    Eigen::VectorXd weights;
    updateDistribution(distribution, samples, costs, weights, distribution_new);     
  }
  
  /** Update a distribution given the samples and costs of an epoch.
   * \param[in] distribution Current distribution
   * \param[in] samples The samples in the epoch (size: n_samples X n_dims)
   * \param[in] costs Costs of the samples (size: n_samples x 1)
   * \param[out] distribution_new Updated distribution
   * \param[out] summary An object containing all relevant update information, for logging and debugging purposes.
   */
  inline void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, DistributionGaussian& distribution_new, UpdateSummary& summary) 
  {
    Eigen::VectorXd weights;
    updateDistribution(distribution, samples, costs, weights, distribution_new, summary);     
  }
  
  /** Update a distribution given the samples and costs of an epoch.
   * \param[in] distribution Current distribution
   * \param[in] samples The samples in the epoch (size: n_samples X n_dims)
   * \param[in] costs Costs of the samples (size: n_samples x 1)
   * \param[out] weights The weights computed from the costs
   * \param[out] distribution_new Updated distribution
   */
  virtual void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, Eigen::VectorXd& weights, DistributionGaussian& distribution_new) const = 0;
};

#endif
