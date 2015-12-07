/**
 * @file   UpdateSummary.h
 * @brief  UpdateSummary class header file.
 * @author Freek Stulp
 */

#ifndef UPDATESUMMARY_H
#define UPDATESUMMARY_H   

#include <string>
#include <vector>
#include <eigen3/Eigen/Core>

// Forward declaration
class DistributionGaussian;

// POD class, http://en.wikipedia.org/wiki/Plain_old_data_structure
/** POD class for storing the information relevant to a distribution update. 
 * Used for logging purposes.
 * This is a "plain old data" class, i.e. all member variables are public
 */
class UpdateSummary {
public:
  /** Distribution before update. */
  DistributionGaussian* distribution;
  /** Samples in the epoch. */
  Eigen::MatrixXd samples;
  /** Cost of the evaluation sample */
  double cost_eval;
  /** Costs of the samples in the epoch. */
  Eigen::VectorXd costs;
  /** Weights of the samples in the epoch, computed from their costs. */
  Eigen::MatrixXd weights;
  /** Distribution after the update. */
  DistributionGaussian* distribution_new;
  
};

/**
 * Save an update summary to a directory
 * \param[in] update_summary Object to write
 * \param[in] directory Directory to which to write object
 * \param[in] i_parallel Optional number appended to filename (useful when running multiple parallel optimizations).
 *  \return true if saving the UpdateSummary was successful, false otherwise
 */
bool saveToDirectory(const UpdateSummary& update_summary, std::string directory, int i_parallel=0);

#endif

