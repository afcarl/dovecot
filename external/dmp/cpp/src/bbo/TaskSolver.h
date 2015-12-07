/**
 * @file   TaskSolver.h
 * @brief  TaskSolver class header file.
 * @author Freek Stulp
 */
 
#ifndef TASK_SOLVER_H
#define TASK_SOLVER_H

#include <eigen3/Eigen/Core>

/** Interface for classes that can perform rollouts.
 * For further information see the section on \ref sec_bbo_task_and_task_solver
 */
class TaskSolver
{
public:
  /** Perform rollouts, i.e. given a set of samples, determine all the variables that are relevant to evaluating the cost function. 
   * \param[in] samples The samples
   * \param[out] cost_vars The variables relevant to computing the cost.
   * \todo Compare to other functions
   */
  inline void performRollouts(const Eigen::MatrixXd& samples, Eigen::MatrixXd& cost_vars) const
  {
    Eigen::MatrixXd task_parameters(0,0);
    performRollouts(samples,task_parameters,cost_vars);
  };
    
  /** Perform rollouts, i.e. given a set of samples, determine all the variables that are relevant to evaluating the cost function. 
   * \param[in] samples The samples
   * \param[in] task_parameters The parameters of the task
   * \param[out] cost_vars The variables relevant to computing the cost.
   * \todo Compare to other functions
   */
  virtual void performRollouts(const Eigen::MatrixXd& samples, const Eigen::MatrixXd& task_parameters, Eigen::MatrixXd& cost_vars) const = 0;
  
  //void performRollouts(const Eigen::MatrixXd& samples, Eigen::MatrixXd& cost_vars) const 
  //{
  //  Eigen::MatrixXd task_parameters(0,0);
  //  performRollouts(samples,task_parameters,cost_vars);
  //}
  
  // virtual void performRollouts(const std::vector<Eigen::MatrixXd>& samples, const Eigen::MatrixXd& task_parameters, Eigen::MatrixXd& cost_vars) const = 0;
  
  /** Write to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output stream to which the object was written
   */
  virtual std::ostream& serialize(std::ostream& output) const = 0;

  /** Print a TaskSolver to an output stream. 
   *
   *  \param[in] output  Output stream to which to write to
   *  \param[in] task_solver TaskSolver to write
   *  \return    Output stream
   *
   *  \remark Calls virtual function TaskSolver::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const TaskSolver& task_solver) {
    return task_solver.serialize(output);
  }
  
};

#endif

