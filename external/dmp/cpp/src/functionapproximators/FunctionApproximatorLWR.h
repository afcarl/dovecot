/**
 * @file   FunctionApproximatorLWR.h
 * @brief  FunctionApproximatorLWR class header file.
 * @author Freek Stulp
 */

#ifndef _FUNCTION_APPROXIMATOR_LWR_H_
#define _FUNCTION_APPROXIMATOR_LWR_H_

#include "functionapproximators/FunctionApproximator.h"

// Forward declarations
class MetaParametersLWR;
class ModelParametersLWR;

/** @defgroup LWR Locally Weighted Regression (LWR)
 *  @ingroup FunctionApproximators
 */

/** \brief LWR (Locally Weighted Regression) function approximator
 * \ingroup FunctionApproximators
 * \ingroup LWR  
 */
class FunctionApproximatorLWR : public FunctionApproximator
{
public:
  
  /** Initialize a function approximator with meta- and optionally model-parameters
   *  \param[in] meta_parameters  The training algorithm meta-parameters
   *  \param[in] model_parameters The parameters of the trained model. If this parameter is not
   *                              passed, the function approximator is initialized as untrained. 
   *                              In this case, you must call FunctionApproximator::train() before
   *                              being able to call FunctionApproximator::predict().
   */
  FunctionApproximatorLWR(MetaParametersLWR *meta_parameters, ModelParametersLWR *model_parameters=NULL);  

  /** Initialize a function approximator with model parameters
   *  \param[in] model_parameters The parameters of the (previously) trained model.
   */
  FunctionApproximatorLWR(ModelParametersLWR *model_parameters);

	FunctionApproximator* clone(void) const;
  
	void train(const Eigen::MatrixXd& input, const Eigen::MatrixXd& target);

	void predict(const Eigen::MatrixXd& input, Eigen::MatrixXd& output);
  
	inline std::string getName(void) const {
    return std::string("LWR");  
  };
  
};


#endif // _FUNCTION_APPROXIMATOR_LWR_H_


