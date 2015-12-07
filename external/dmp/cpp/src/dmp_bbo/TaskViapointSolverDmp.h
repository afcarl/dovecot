#ifndef TASKVIAPOINTSOLVERDMP_H
#define TASKVIAPOINTSOLVERDMP_H

#include <string>
#include <set>
#include <eigen3/Eigen/Core>

#include "dmp_bbo/TaskSolverParallel.h"

// Forward definition
class Dmp;

class TaskViapointSolverDmp : public TaskSolverParallel
{
private:
  Dmp* dmp_;
  int n_time_steps_;
  double integrate_time_;
  bool use_normalized_parameter_;
  
public:
  TaskViapointSolverDmp(Dmp* dmp, std::set<std::string> optimize_parameters, double dt=0.01, double integrate_dmp_beyond_tau_factor=1.0, bool use_normalized_parameter=false);
    
  virtual void performRollouts(const std::vector<Eigen::MatrixXd>& samples, const Eigen::MatrixXd& task_parameters, Eigen::MatrixXd& cost_vars) const;
  
  std::ostream& serialize(std::ostream& output) const;
  
};

#endif