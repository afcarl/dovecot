/**
 * @file   CostFunction.h
 * @brief  CostFunction class header file.
 * @author Freek Stulp
 */

#ifndef COSTFUNCTION_H
#define COSTFUNCTION_H

#include <vector>
#include <eigen3/Eigen/Core>

/** Interface for cost functions, which define a cost_function.
 * For further information see the section on \ref sec_bbo_task_and_task_solver
 */
class CostFunction
{
public:
  /** The cost function which defines the cost_function.
   *
   * \param[in] samples The samples 
   * \param[out] costs The scalar cost for each sample.
   */
  virtual void evaluate(const Eigen::MatrixXd& samples, Eigen::VectorXd& costs) const 
  {
    int n_cost_function_pars = 0;
    Eigen::MatrixXd cost_function_parameters(samples.rows(),n_cost_function_pars);
    return evaluate(samples,cost_function_parameters, costs);
  };
  
  /** The cost function which defines the cost_function.
   *
   * \param[in] samples The samples 
   * \param[in] cost_function_parameters Optional parameters of the cost_function, and thus the cost function.
   * \param[out] costs The scalar cost for each sample.
   */
  virtual void evaluate(const Eigen::MatrixXd& samples, const Eigen::MatrixXd& cost_function_parameters, Eigen::VectorXd& costs) const = 0;
  
  
  /** Write to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output to which the object was written 
   */
  virtual std::ostream& serialize(std::ostream& output) const = 0;

  /** Write to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \param[in] cost_function CostFunction object to write
   *  \return Output to which the object was written 
   *
   *  \remark Calls virtual function CostFunction::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const CostFunction& cost_function) {
    return cost_function.serialize(output);
  }
};

#endif

