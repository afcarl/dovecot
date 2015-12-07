/**
 * @file DmpContextualTwoStep.h
 * @brief  Contextual Dmp class header file.
 * @author Freek Stulp
 */

#ifndef _DMP_CONTEXTUAL_TWO_STEP_H_
#define _DMP_CONTEXTUAL_TWO_STEP_H_

#include "dmp/DmpContextual.h"

#include <set>

class FunctionApproximator;
class FunctionApproximatorLWR;

/** \defgroup Dmps Dynamic Movement Primitives
 */

/** 
 * \brief Implementation of Contextual Dynamical Movement Primitives.
 * \ingroup Dmps
 */
class DmpContextualTwoStep : public DmpContextual
{
public:
  
  /**
   *  Initialization constructor for Contextual DMPs of known dimensionality, but with unknown
   *  initial and attractor states. Initializes the DMP with default dynamical systems.
   *  \param n_dims_dmp      Dimensionality of the DMP
   *  \param function_approximators Function approximators for the forcing term
   *  \param policy_parameter_function Function approximators for the policy parameter function
   *  \param dmp_type  The type of DMP, see Dmp::DmpType    
   */
  DmpContextualTwoStep(int n_dims_dmp, std::vector<FunctionApproximator*> function_approximators, FunctionApproximator* policy_parameter_function, DmpType dmp_type=KULVICIUS_2012_JOINING);
  
  // Overloads Dmp::computeFunctionApproximatorOutput
  void computeFunctionApproximatorOutput(const Eigen::MatrixXd& phase_state, Eigen::MatrixXd& fa_output) const;

  // Overloads Dmp::train
  void  train(const std::vector<Trajectory>& trajectories, const std::vector<Eigen::MatrixXd>& task_parameters, std::string save_directory);
  
  /** Return whether the DMP is trained or not.
   * \return true if the DMP is trained, false otherwise 
   */
  bool isTrained(void) const;

  
private:
  std::vector<std::vector<FunctionApproximator*> > policy_parameter_function_;

};

#endif