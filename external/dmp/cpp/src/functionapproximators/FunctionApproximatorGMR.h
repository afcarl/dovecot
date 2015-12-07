/**
 * @file FunctionApproximatorGMR.h
 * @brief FunctionApproximatorGMR class header file.
 * @author Thibaut Munzer, Freek Stulp
 */

#ifndef _FUNCTION_APPROXIMATOR_GMR_H_
#define _FUNCTION_APPROXIMATOR_GMR_H_

#include "functionapproximators/FunctionApproximator.h"

// Forward declarations
class MetaParametersGMR;
class ModelParametersGMR;

/** @defgroup GMR Gaussian Mixture Regression (GMR)
 *  @ingroup FunctionApproximators
 */

/** \brief GMR (Gaussian Mixture Regression) function approximator
 * \ingroup FunctionApproximators
 * \ingroup GMR
 */
class FunctionApproximatorGMR : public FunctionApproximator
{
public:
  /** Initialize a function approximator with meta- and optionally model-parameters
   *  \param[in] meta_parameters  The training algorithm meta-parameters
   *  \param[in] model_parameters The parameters of the trained model. If this parameter is not
   *                              passed, the function approximator is initialized as untrained. 
   *                              In this case, you must call FunctionApproximator::train() before
   *                              being able to call FunctionApproximator::predict().
   */
  FunctionApproximatorGMR(MetaParametersGMR* meta_parameters, ModelParametersGMR* model_parameters=NULL);
  
  /** Initialize a function approximator with model parameters
   *  \param[in] model_parameters The parameters of the (previously) trained model.
   */
	FunctionApproximatorGMR(ModelParametersGMR* model_parameters);

	virtual FunctionApproximator* clone(void) const;
	
	void train(const Eigen::MatrixXd& input, const Eigen::MatrixXd& target);
  
	void predict(const Eigen::MatrixXd& input, Eigen::MatrixXd& output);

	std::string getName(void) const {
    return std::string("GMR");  
  };

protected:
  /** Initialize Gaussian for EM algorithm using k-means. 
   * \param[in]  data A data matrix (n_exemples x (n_in_dim + n_out_dim))
   * \param[out]  centers A list (std::vector) of n_gaussian non initiallized centers (n_in_dim + n_out_dim)
   * \param[out]  priors A list (std::vector) of n_gaussian non initiallized priors
   * \param[out]  covars A list (std::vector) of n_gaussian non initiallized covariance matrices ((n_in_dim + n_out_dim) x (n_in_dim + n_out_dim))
   * \param[in]  nbMaxIter The maximum number of iterations
   */
  void _kMeansInit(const Eigen::MatrixXd& data, std::vector<Eigen::VectorXd*>& centers, std::vector<double*>& priors,
    std::vector<Eigen::MatrixXd*>& covars, int nbMaxIter=1000);

  /** EM algorithm. 
   * \param[in] data A (n_exemples x (n_in_dim + n_out_dim)) data matrix
   * \param[in,out] centers A list (std::vector) of n_gaussian centers (vector of size (n_in_dim + n_out_dim))
   * \param[in,out] priors A list (std::vector) of n_gaussian priors
   * \param[in,out] covars A list (std::vector) of n_gaussian covariance matrices ((n_in_dim + n_out_dim) x (n_in_dim + n_out_dim))
   * \param[in] nbMaxIter The maximum number of iterations
   */
  void _EM(const Eigen::MatrixXd& data, std::vector<Eigen::VectorXd*>& centers, std::vector<double*>& priors,
    std::vector<Eigen::MatrixXd*>& covars, int nbMaxIter=200);
  

  /** Compute P(data), data ~ N(center, covar)
   * \param[in] data A vector
   * \param[in] center The mean of the normal distribution
   * \param[in] cov The covariance of the normal distribution 
   * \return the probability p(data)
   */
 double _normal(const Eigen::VectorXd& data, const Eigen::VectorXd& center, const Eigen::MatrixXd& cov);
};

#endif // !_FUNCTION_APPROXIMATOR_GMR_H_
