/**
 * @file FunctionApproximatorGMR.hpp
 * @brief FunctionApproximatorGMR class header file.
 * @author Thibaut Munzer, Freek Stulp
 *
 * This file is part of DmpBbo, a set of libraries and programs for the 
 * black-box optimization of dynamical movement primitives.
 * Copyright (C) 2014 Freek Stulp, ENSTA-ParisTech
 * 
 * DmpBbo is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 * 
 * DmpBbo is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with DmpBbo.  If not, see <http://www.gnu.org/licenses/>. 
 */

#ifndef _FUNCTION_APPROXIMATOR_GMR_H_
#define _FUNCTION_APPROXIMATOR_GMR_H_

#include "functionapproximators/FunctionApproximator.hpp"


/** @defgroup GMR Gaussian Mixture Regression (GMR)
 *  @ingroup FunctionApproximators
 */
 
namespace DmpBbo {

  // Forward declarations
class MetaParametersGMR;
class ModelParametersGMR;

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

	void predictVariance(const Eigen::MatrixXd& inputs, Eigen::MatrixXd& variances);
	
	std::string getName(void) const {
    return std::string("GMR");  
  };

protected:
  /** Initialize Gaussian for EM algorithm using k-means. 
   * \param[in]  data A data matrix (n_exemples x (n_in_dim + n_out_dim))
   * \param[out]  means A list (std::vector) of n_gaussian non initiallized means (n_in_dim + n_out_dim)
   * \param[out]  priors A list (std::vector) of n_gaussian non initiallized priors
   * \param[out]  covars A list (std::vector) of n_gaussian non initiallized covariance matrices ((n_in_dim + n_out_dim) x (n_in_dim + n_out_dim))
   * \param[in]  n_max_iter The maximum number of iterations
   * \author Thibaut Munzer
   */
  void kMeansInit(const Eigen::MatrixXd& data, std::vector<Eigen::VectorXd>& means, std::vector<double>& priors,
    std::vector<Eigen::MatrixXd>& covars, int n_max_iter=1000);

  /** Initialize Gaussian for EM algorithm using a same-size slicing on the first dimension (method used in Calinon GMR implementation).
   * Particulary suited when input is 1-D and data distribution is uniform over input dimension
   * \param[in]  data A data matrix (n_exemples x (n_in_dim + n_out_dim))
   * \param[out]  means A list (std::vector) of n_gaussian non initiallized means (n_in_dim + n_out_dim)
   * \param[out]  priors A list (std::vector) of n_gaussian non initiallized priors
   * \param[out]  covars A list (std::vector) of n_gaussian non initiallized covariance matrices ((n_in_dim + n_out_dim) x (n_in_dim + n_out_dim))
   * \author Thibaut Munzer
   */
  void firstDimSlicingInit(const Eigen::MatrixXd& data, std::vector<Eigen::VectorXd>& means, std::vector<double>& priors,
    std::vector<Eigen::MatrixXd>& covars);

  /** EM algorithm. 
   * \param[in] data A (n_exemples x (n_in_dim + n_out_dim)) data matrix
   * \param[in,out] means A list (std::vector) of n_gaussian means (vector of size (n_in_dim + n_out_dim))
   * \param[in,out] priors A list (std::vector) of n_gaussian priors
   * \param[in,out] covars A list (std::vector) of n_gaussian covariance matrices ((n_in_dim + n_out_dim) x (n_in_dim + n_out_dim))
   * \param[in] n_max_iter The maximum number of iterations
   * \author Thibaut Munzer
   */
  void expectationMaximization(const Eigen::MatrixXd& data, std::vector<Eigen::VectorXd>& means, std::vector<double>& priors,
    std::vector<Eigen::MatrixXd>& covars, int n_max_iter=50);
  

  /** The probability density function (PDF) of the multi-variate normal distribution
   * \param[in] data A vector
   * \param[in] mu The mean of the normal distribution
   * \param[in] covar The covariance of the normal distribution 
   * \return the probability
   */
  static double normalPDF(const Eigen::VectorXd& mu, const Eigen::MatrixXd& covar, const Eigen::VectorXd& input);
 
  static double normalPDFWithInverseCovar(const Eigen::VectorXd& mu, const Eigen::MatrixXd& covar_inverse, const Eigen::VectorXd& input);

  void computeProbabilities(const ModelParametersGMR* gmm, const Eigen::VectorXd& input, Eigen::VectorXd& h) const;

private:
  /**
   * Default constructor.
   * \remarks This default constuctor is required for boost::serialization to work. Since this
   * constructor should not be called by other classes, it is private (boost::serialization is a
   * friend)
   */
  FunctionApproximatorGMR(void) {};
  
  /** Give boost serialization access to private members. */  
  friend class boost::serialization::access;
  
  /** Serialize class data members to boost archive. 
   * \param[in] ar Boost archive
   * \param[in] version Version of the class
   * See http://www.boost.org/doc/libs/1_55_0/libs/serialization/doc/tutorial.html#simplecase
   */
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);

};

}

#include <boost/serialization/export.hpp>
/** Register this derived class. */
BOOST_CLASS_EXPORT_KEY2(DmpBbo::FunctionApproximatorGMR, "FunctionApproximatorGMR")

/** Don't add version information to archives. */
BOOST_CLASS_IMPLEMENTATION(DmpBbo::FunctionApproximatorGMR,boost::serialization::object_serializable);

#endif // !_FUNCTION_APPROXIMATOR_GMR_H_
