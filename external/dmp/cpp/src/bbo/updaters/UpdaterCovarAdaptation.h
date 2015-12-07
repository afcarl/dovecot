/**
 * @file   UpdaterCovarAdaptation.h
 * @brief  UpdaterCovarAdaptation class header file.
 * @author Freek Stulp
 */

#ifndef UPDATERCOVARADAPTATION_H
#define UPDATERCOVARADAPTATION_H

#include <string>
#include <eigen3/Eigen/Core>

#include "bbo/updaters/UpdaterMean.h"

/** Updater that updates the mean and also implements Covariance Matrix Adaptation.
 * The update rule is as in <A HREF="http://en.wikipedia.org/wiki/CMA-ES">CMA-ES</A>, except that this version does not use the evolution paths.
 *
 */
class UpdaterCovarAdaptation : public UpdaterMean
{
public:
  
  /** Constructor
   * \param[in] eliteness The eliteness parameter ('mu' in CMA-ES, 'h' in PI^2)
   * \param[in] weighting_method ('PI-BB' = PI^2 style weighting)
   * \param[in] base_level Small covariance matrix that is added after each update to avoid premature convergence
   * \param[in] diag_only Update only the diagonal of the covariance matrix (true) or the full matrix (false)
   * \param[in] learning_rate Low pass filter on the covariance updates. In range [0.0-1.0] with 0.0 = no updating, 1.0  = complete update by ignoring previous covar matrix. 
   */
  UpdaterCovarAdaptation(double eliteness, std::string weighting_method="PI-BB", const Eigen::VectorXd& base_level=Eigen::VectorXd::Zero(0), bool diag_only=true, double learning_rate=1.0);
  
  void updateDistribution(const DistributionGaussian& distribution, const Eigen::MatrixXd& samples, const Eigen::VectorXd& costs, Eigen::VectorXd& weights, DistributionGaussian& distribution_new) const;
  
private:
  bool diag_only_;
  double learning_rate_;
  Eigen::MatrixXd base_level_as_diagonal_matrix_;
 
};
    
#endif
