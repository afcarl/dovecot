/**
 * @file FunctionApproximatorIRFRLS.h
 * @brief FunctionApproximatorIRFRLS class header file.
 * @author Thibaut Munzer, Freek Stulp
 */

#ifndef _FUNCTION_APPROXIMATOR_IRFRLS_H_
#define _FUNCTION_APPROXIMATOR_IRFRLS_H_

#include "functionapproximators/FunctionApproximator.h"

// Forward declarations
class MetaParametersIRFRLS;
class ModelParametersIRFRLS;

/** @defgroup IRFRLS Incremental Random Features Regularized Least Squares (iRFRLS)
 *  @ingroup FunctionApproximators
 */

/** \brief iRFRLS (Incremental Random Features Regularized Least Squares) function approximator
 * \ingroup FunctionApproximators
 * \ingroup IRFRLS
 */
class FunctionApproximatorIRFRLS : public FunctionApproximator
{
public:
  /** Initialize a function approximator with meta- and optionally model-parameters
   *  \param[in] meta_parameters  The training algorithm meta-parameters
   *  \param[in] model_parameters The parameters of the trained model. If this parameter is not
   *                              passed, the function approximator is initialized as untrained. 
   *                              In this case, you must call FunctionApproximator::train() before
   *                              being able to call FunctionApproximator::predict().
   */
  FunctionApproximatorIRFRLS(MetaParametersIRFRLS* meta_parameters, ModelParametersIRFRLS* model_parameters=NULL);
  
  /** Initialize a function approximator with model parameters
   *  \param[in] model_parameters The parameters of the (previously) trained model.
   */
	FunctionApproximatorIRFRLS(ModelParametersIRFRLS* model_parameters);

	virtual FunctionApproximator* clone(void) const;
	
	void train(const Eigen::MatrixXd& input, const Eigen::MatrixXd& target);
	void predict(const Eigen::MatrixXd& input, Eigen::MatrixXd& output);

	std::string getName(void) const {
    return std::string("IRFRLS");  
  };

protected:
  /** Project data with cosines features
   * \param[in] vecs The vector to be projected
   * \param[in] periods Periods of the cosines
   * \param[in] phases phases of the cosines
   * \param[out] projected the projected values of vecs
   */
  void proj(const Eigen::MatrixXd& vecs, const Eigen::MatrixXd& periods, const Eigen::VectorXd& phases, Eigen::MatrixXd& projected);
};

#endif // !_FUNCTION_APPROXIMATOR_IRFRLS_H_
