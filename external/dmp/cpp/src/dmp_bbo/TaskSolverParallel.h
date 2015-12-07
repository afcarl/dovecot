#ifndef TASK_SOLVER_PARALLEL_H
#define TASK_SOLVER_PARALLEL_H

#include "bbo/TaskSolver.h"

#include <vector>
#include <eigen3/Eigen/Core>

/** Interface for classes that can perform rollouts.
 * For further information see the section on \ref sec_bbo_task_and_task_solver
 */
 class TaskSolverParallel : public TaskSolver
{
public:
    
  /** Perform rollouts, i.e. given a set of samples, determine all the variables that are relevant to evaluating the cost function. 
   * \param[in] samples The samples
   * \param[in] task_parameters The parameters of the task
   * \param[out] cost_vars The variables relevant to computing the cost.
   * \todo Compare to other functions
   */
  inline void performRollouts(const Eigen::MatrixXd& samples, const Eigen::MatrixXd& task_parameters, Eigen::MatrixXd& cost_vars) const 
  {
    std::vector<Eigen::MatrixXd> samples_vec(1);
    samples_vec[0] = samples;
    performRollouts(samples_vec, cost_vars);
  };
  
  /** Perform rollouts, i.e. given a set of samples, determine all the variables that are relevant
   * to evaluating the cost function. 
   * This version does so for parallel optimization, where multiple distributions are updated.
   * \param[in] samples_vec The samples, a vector with one element per distribution
   * \param[out] cost_vars The variables relevant to computing the cost.
   * \todo Compare to other functions
   */
  void performRollouts(const std::vector<Eigen::MatrixXd>& samples_vec, Eigen::MatrixXd& cost_vars) const 
  {
    Eigen::MatrixXd task_parameters(0,0);
    performRollouts(samples_vec,task_parameters,cost_vars);
  }
  
  /** Perform rollouts, i.e. given a set of samples, determine all the variables that are relevant
   * to evaluating the cost function. 
   * This version does so for parallel optimization, where multiple distributions are updated.
   * \param[in] samples_vec The samples, a vector with one element per distribution
   * \param[in] task_parameters The parameters of the task
   * \param[out] cost_vars The variables relevant to computing the cost.
   * \todo Compare to other functions
   */
  virtual void performRollouts(const std::vector<Eigen::MatrixXd>& samples_vec, const Eigen::MatrixXd& task_parameters, Eigen::MatrixXd& cost_vars) const = 0;
  
  /** Print a TaskSolver to an output stream. 
   *
   *  \param[in] output  Output stream to which to write to
   *  \param[in] task_solver TaskSolver to write
   *  \return    Output stream
   *
   *  \remark Calls virtual function TaskSolver::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const TaskSolverParallel& task_solver) {
    return task_solver.serialize(output);
  }
  
};

#endif

