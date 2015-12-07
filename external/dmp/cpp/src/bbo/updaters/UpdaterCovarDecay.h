/**
 * @file   UpdaterCovarDecay.h
 * @brief  UpdaterCovarDecay class header file.
 * @author Freek Stulp
 */
 
#ifndef UPDATERCOVARDECAY_H
#define UPDATERCOVARDECAY_H

#include <string>
#include <eigen3/Eigen/Core>

#include "bbo/updaters/UpdaterMean.h"

/** Updater that updates the mean and decreases the size of the covariance matrix over time.
 */
class UpdaterCovarDecay : public UpdaterMean
{
private:
  double covar_decay_factor_;

public:
  /** Constructor
   * \param[in] eliteness The eliteness parameter ('mu' in CMA-ES, 'h' in PI^2)
   * \param[in] covar_decay_factor The covar matrix shrinks at each update with C^new = covar_decay_factor^2 * C. It should be in the range <0-1] 
   * \param[in] weighting_method ('PI-BB' = PI^2 style weighting)
   */
  UpdaterCovarDecay(double eliteness, double covar_decay_factor=0.95, std::string weighting_method="PI-BB");
  
  void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, Eigen::VectorXd& weights, DistributionGaussian& distribution_new) const;
};
    
#endif
