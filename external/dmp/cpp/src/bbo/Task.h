/**
 * @file   Task.h
 * @brief  Task class header file.
 * @author Freek Stulp
 */
 
#ifndef TASK_H
#define TASK_H

#include <vector>
#include <eigen3/Eigen/Core>

/** Interface for cost functions, which define a task.
 * For further information see the section on \ref sec_bbo_task_and_task_solver
 */
class Task
{
public:
  /** The cost function which defines the task.
   *
   * \param[in] cost_vars All the variables relevant to computing the cost. These are determined by TaskSolver::performRollouts(). For further information see the section on \ref sec_bbo_task_and_task_solver
   * \param[out] costs The scalar cost for each sample.
   */
  virtual void evaluate(const Eigen::MatrixXd& cost_vars, Eigen::VectorXd& costs) const 
  {
    int n_task_pars = 0;
    Eigen::MatrixXd task_parameters(cost_vars.rows(),n_task_pars);
    return evaluate(cost_vars,task_parameters, costs);
  };
  
  /** The cost function which defines the task.
   *
   * \param[in] cost_vars All the variables relevant to computing the cost. These are determined by TaskSolver::performRollouts(). For further information see the section on \ref sec_bbo_task_and_task_solver
   * \param[in] task_parameters Optional parameters of the task, and thus the cost function.
   * \param[out] costs The scalar cost for each sample.
   */
  virtual void evaluate(const Eigen::MatrixXd& cost_vars, const Eigen::MatrixXd& task_parameters, Eigen::VectorXd& costs) const = 0;
  
  /** Save a python script that is able to visualize the rollouts, given the cost-relevant variables
   *  stored in a file.
   *  \param[in] directory Directory in which to save the python script
   *  \return true if saving the script was successful, false otherwise
   */
  virtual bool savePerformRolloutsPlotScript(std::string directory)
  {
    return true;
  }
  
  /** Write to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output to which the object was written 
   */
  virtual std::ostream& serialize(std::ostream& output) const = 0;

  /** Write to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \param[in] task Task object to write
   *  \return Output to which the object was written 
   *
   *  \remark Calls virtual function Task::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const Task& task) {
    return task.serialize(output);
  }
};

#endif

