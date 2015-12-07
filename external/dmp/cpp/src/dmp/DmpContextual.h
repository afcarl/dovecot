/**
 * @file DmpContextual.h
 * @brief  Contextual Dmp class header file.
 * @author Freek Stulp
 */

#ifndef _DMP_CONTEXTUAL_H_
#define _DMP_CONTEXTUAL_H_

#include "dmp/Dmp.h"

#include <set>

class FunctionApproximator;

/** \defgroup Dmps Dynamic Movement Primitives
 */

/** 
 * \brief Implementation of Contextual Dynamical Movement Primitives.
 *
 * Contextual Dmp extends a 'standard' Dmp by adapting to task parameters.

This is how a 'standard' Dmp would be integrated
\code 
VectorXd x, xd, x_updated;
dmp->integrateStart(x,xd);
for (int t=1; t<T; t++) {
  dmp->integrateStep(dt,x,x_updated,xd); 
  x = x_updated;
}
\endcode 

A contextual Dmp is integrated as follows.
\code 
VectorXd x, xd, x_updated;
dmp->set_task_parameters(some_task_parameters);
dmp->integrateStart(x,xd);
for (int t=1; t<T; t++) {
  dmp->integrateStep(dt,x,x_updated,xd); 
  x = x_updated;
}
\endcode 

Or, if the task parameters change over time.
\code
VectorXd x, xd, x_updated;
dmp->integrateStart(x,xd);
for (int t=1; t<T; t++) {
  dmp->set_task_parameters(some_task_parameters);
  dmp->integrateStep(dt,x,x_updated,xd); 
  x = x_updated;
}
\endcode 
 * \ingroup Dmps
 */
class DmpContextual : public Dmp
{
public:
  
  /**
   *  Initialization constructor for Contextual DMPs of known dimensionality, but with unknown
   *  initial and attractor states. Initializes the DMP with default dynamical systems.
   *  \param n_dims_dmp      Dimensionality of the DMP
   *  \param function_approximators Function approximators for the forcing term
   *  \param dmp_type  The type of DMP, see Dmp::DmpType    
   */
  DmpContextual(int n_dims_dmp, std::vector<FunctionApproximator*> function_approximators, DmpType dmp_type);
  
  /** Set the current task parameters.
   * \param[in] task_parameters Current task parameters
   */
  inline void set_task_parameters(const Eigen::MatrixXd& task_parameters)
  {
    assert(task_parameters_.cols()==task_parameters.cols());
    task_parameters_ = task_parameters; 
  }
  
  // Overrides Dmp::computeFunctionApproximatorOutput
  virtual void computeFunctionApproximatorOutput(const Eigen::MatrixXd& phase_state, Eigen::MatrixXd& fa_output) const = 0;

  /** Train a contextual Dmp with a set of trajectories (and save results to file)
   * This function is useful for debugging, i.e. if you want to save intermediate results to a
   * directory
   * \param[in] trajectories The set of trajectories
   * \param[in] task_parameters The task parameters for each of the trajectories.
   * \param[in] save_directory Directory to which to save intermediate results.
   * Overloads Dmp::train
   */
  virtual void  train(const std::vector<Trajectory>& trajectories, const std::vector<Eigen::MatrixXd>& task_parameters, std::string save_directory) = 0;
  
  /** Train a contextual DMP with multiple trajectories
   * \param[in] trajectories A set of demonstrated trajectories 
   */
  void  train(const std::vector<Trajectory>& trajectories);

  /** Train a contextual DMP with multiple trajectories
   * \param[in] trajectories A set of demonstrated trajectories 
   * \param[in] save_directory Directory to which to save intermediate results
   */
  virtual void train(const std::vector<Trajectory>& trajectories, std::string save_directory);
  
  /** Train a contextual DMP with multiple trajectories
   * \param[in] trajectories A set of demonstrated trajectories 
   * \param[in] task_parameters The task_parameters for each trajectory. It is a std::vector, where each task parameter element corresponds to one Trajectory. Each element is a matrix of size n_time_steps x n_task_paramaters 
   */
  virtual void train(const std::vector<Trajectory>& trajectories, const std::vector<Eigen::MatrixXd>& task_parameters);
  
protected:
  /** The current task parameters.
   */
  Eigen::MatrixXd task_parameters_;

  /** Check if several trajectories have the same duration and initial/final states.
   * \param[in] trajectories A set of trajectories 
   */  
  void checkTrainTrajectories(const std::vector<Trajectory>& trajectories);

};

#endif