/**
 * @file   FunctionApproximatorLWPR.h
 * @brief  FunctionApproximatorLWPR class header file.
 * @author Freek Stulp
 */

#ifndef _FUNCTION_APPROXIMATOR_LWPR_H_
#define _FUNCTION_APPROXIMATOR_LWPR_H_

#include "functionapproximators/FunctionApproximator.h"

// Forward declarations
class MetaParametersLWPR;
class ModelParametersLWPR;

/** @defgroup LWPR Locally Weighted Projection Regression (LWPR)
 *  @ingroup FunctionApproximators
 */
 
/** \brief LWPR (Locally Weighted Projection Regression) function approximator
 * \ingroup FunctionApproximators
 * \ingroup LWPR
 */
class FunctionApproximatorLWPR : public FunctionApproximator
{
public:

  /** Initialize a function approximator with meta- and optionally model-parameters
   *  \param[in] meta_parameters  The training algorithm meta-parameters
   *  \param[in] model_parameters The parameters of the trained model. If this parameter is not
   *                              passed, the function approximator is initialized as untrained. 
   *                              In this case, you must call FunctionApproximator::train() before
   *                              being able to call FunctionApproximator::predict().
   */
  FunctionApproximatorLWPR(MetaParametersLWPR *meta_parameters, ModelParametersLWPR *model_parameters=NULL); 
  
  /** Initialize a function approximator with model parameters
   *  \param[in] model_parameters The parameters of the (previously) trained model.
   */
  FunctionApproximatorLWPR(ModelParametersLWPR *model_parameters);
	
	FunctionApproximator* clone(void) const;
	
	void train(const Eigen::MatrixXd& input, const Eigen::MatrixXd& target);
	void predict(const Eigen::MatrixXd& input, Eigen::MatrixXd& output);

	std::string getName(void) const {
    return std::string("LWPR");  
  };
  
};

#endif // _FUNCTION_APPROXIMATOR_LWPR_H_
