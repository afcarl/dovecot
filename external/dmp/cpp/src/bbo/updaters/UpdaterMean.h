/**
 * @file   UpdaterMean.h
 * @brief  UpdaterMean class header file.
 * @author Freek Stulp
 */

#ifndef UPDATERMEAN_H
#define UPDATERMEAN_H   

#include <string>
#include <eigen3/Eigen/Core>

#include "bbo/Updater.h"

/** Updater that updates the mean (but not the covariance matrix) of the parameter distribution.
 */
class UpdaterMean : public Updater
{
public:
  
  /** Constructor
   * \param[in] eliteness The eliteness parameter ('mu' in CMA-ES, 'h' in PI^2)
   * \param[in] weighting_method ('PI-BB' = PI^2 style weighting)
   */
  UpdaterMean(double eliteness, std::string weighting_method="PI-BB");
  
  virtual void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, Eigen::VectorXd& weights, DistributionGaussian& distribution_new) const;
  
  /** Update the distribution mean
   * \param[in] mean Current mean
   * \param[in] samples The samples in the epoch (size: n_samples X n_dims)
   * \param[in] costs Costs of the samples (size: n_samples x 1)
   * \param[out] weights The weights computed from the costs
   * \param[out] mean_new Updated mean
   */ 
  void updateDistributionMean(const Eigen::VectorXd& mean, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, Eigen::VectorXd& weights, Eigen::VectorXd& mean_new) const;

  /** Convert costs to weights, given the weighting method.
   *  The weights should sum to 1, and higher costs should lead to lower weights.
   * \param[in] costs Costs of the samples (size: n_samples x 1)
   * \param[in] weighting_method ('PI-BB' = PI^2 style weighting)
   * \param[in] eliteness The eliteness parameter ('mu' in CMA-ES, 'h' in PI^2)
   * \param[out] weights The weights computed from the costs
   */
  void costsToWeights(const Eigen::VectorXd& costs, std::string weighting_method, double eliteness, Eigen::VectorXd& weights) const;
  
protected:
  /** Eliteness parameters ('mu' in CMA-ES, 'h' in PI^2) */
  double eliteness_;
  /** Weighting method */
  std::string weighting_method_;

};
    
#endif
