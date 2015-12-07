/**
 * @file   DistributionGaussian.h
 * @brief  DistributionGaussian class header file.
 * @author Freek Stulp
 */

#ifndef DISTRIBUTIONGAUSSIAN_H
#define DISTRIBUTIONGAUSSIAN_H   

#include <vector>
#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Cholesky>

#include <boost/random.hpp>

/** \brief A class for representing a Gaussian distribution.
 *
 * This is mainly a wrapper around boost functionality
 * The reason to make the wrapper is to provide functionality for serialization/deserialization.
 */
class DistributionGaussian
{
public:
  /** Construct the Gaussian distribution with a mean and covariance matrix.
   *  \param[in] mean Mean of the distribution
   *  \param[in] covar Covariance matrix of the distribution
   */
  DistributionGaussian(const Eigen::VectorXd& mean, const Eigen::MatrixXd& covar);
  
  /** Generate samples from the distribution.
   *  \param[in] n_samples Number of samples to sample
   *  \param[in] samples the samples themselves (size n_samples X dim(mean)
   */
  void generateSamples(int n_samples, Eigen::MatrixXd& samples);
  
  /** Make a deep copy of the object.
   * \return A deep copy of the object.
   */
  DistributionGaussian* clone(void) const;
  
  /**
   * Accessor get function for the mean.
   * \return The mean of the distribution
   */
  const Eigen::VectorXd& mean(void) const   { return mean_;   }
  
  /**
   * Accessor get function for the covariance matrix.
   * \return The covariance matrix of the distribution
   */
  const Eigen::MatrixXd& covar(void) const { return covar_; }
  
  /**
   * Accessor set function for the mean.
   * \param[in] mean The new mean of the distribution
   */
  void set_mean(const Eigen::VectorXd& mean);
  
  /**
   * Accessor set function for the covar.
   * \param[in] covar The new covariance matrix of the distribution
   */
  void set_covar(const Eigen::MatrixXd& covar);

  
  /** Print to output stream. 
   *
   *  \param[in] output  Output stream to which to write to
   *  \param[in] distribution Distribution to write
   *  \return    Output stream
   */ 
  friend std::ostream& operator<<(std::ostream& output, const DistributionGaussian& distribution)
  {
    distribution.serialize(output);
    return output;
  }

   /** Write object to output stream. 
    *  \param[in] output Output stream to which to write to 
    *  \return Output stream to which the object was written 
    */
  std::ostream& serialize(std::ostream& output) const;
  
private:
  /** Boost's random number generator. Shared by all object instances. */
  static boost::mt19937 rng;
  /** Mean of the distribution */
  Eigen::VectorXd mean_;
  /** Covariance matrix of the distribution */
  Eigen::MatrixXd covar_;  
  /** Cholesky decomposition of the covariance matrix of the distribution. This cached variable makes it easier to generate samples. */
  Eigen::MatrixXd covar_decomposed_;
  
};

#endif
