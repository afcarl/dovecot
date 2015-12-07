#ifndef TASKVIAPOINT_H
#define TASKVIAPOINT_H

#include <eigen3/Eigen/Core>

#include "dmp_bbo/TaskWithTrajectoryDemonstrator.h"

#define NO_VIAPOINT_TIME -1

class TaskViapoint : public TaskWithTrajectoryDemonstrator
{
private:
  
  Eigen::VectorXd viapoint_;
  double   viapoint_time_;
  
  Eigen::VectorXd goal_;
  double   goal_time_;
  
  double   viapoint_weight_;
  double   acceleration_weight_;
  double   goal_weight_;
  
public:
  TaskViapoint(const Eigen::VectorXd& viapoint, double  viapoint_time);
  TaskViapoint(const Eigen::VectorXd& viapoint, double  viapoint_time, const Eigen::VectorXd& goal, double goal_time);
  
  void evaluate(const Eigen::MatrixXd& cost_vars, const Eigen::MatrixXd& task_parameters, Eigen::VectorXd& costs) const;
  
  void setCostFunctionWeighting(double viapoint_weight, double acceleration_weight, double goal_weight=0.0);
  
  void generateDemonstration(const Eigen::MatrixXd& task_parameters, const Eigen::VectorXd& ts, Trajectory& demonstration) const;
  
  std::ostream& serialize(std::ostream& output) const;

};

#endif

