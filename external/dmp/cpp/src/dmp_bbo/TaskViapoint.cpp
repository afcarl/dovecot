#include "dmp_bbo/TaskViapoint.h"

#include <iostream>
#include <iomanip>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

TaskViapoint::TaskViapoint(const VectorXd& viapoint, double  viapoint_time)
: viapoint_(viapoint),   viapoint_time_(viapoint_time), goal_(VectorXd::Zero(viapoint.size())), goal_time_(-1),
  viapoint_weight_(1.0), acceleration_weight_(0.0001),  goal_weight_(0.0)
{
}

TaskViapoint::TaskViapoint(const VectorXd& viapoint, double  viapoint_time,const VectorXd& goal,  double goal_time)
: viapoint_(viapoint),   viapoint_time_(viapoint_time), goal_(goal), goal_time_(goal_time),
  viapoint_weight_(1.0), acceleration_weight_(0.0001),  goal_weight_(1.0)
{
  assert(viapoint_.size()==goal.size());
}
  
void TaskViapoint::evaluate(const MatrixXd& cost_vars, const MatrixXd& task_parameters, VectorXd& costs) const
{
  int n_samples = cost_vars.rows();
  int n_dims = viapoint_.size();
  int n_cost_vars = 4*n_dims + 1; // y_1..y_D  yd_1..yd_D  ydd_1..ydd_D  t forcing_term_1..forcing_term_D
  int n_time_steps = cost_vars.cols()/n_cost_vars;
  // cost_vars  = n_samples x (n_time_steps*n_cost_vars)

  //cout << "  n_samples=" << n_samples << endl;
  //cout << "  n_dims=" << n_dims << endl;
  //cout << "  n_cost_vars=" << n_cost_vars << endl;
  //cout << "  cost_vars.cols()=" << cost_vars.cols() << endl;  
  //cout << "  n_time_steps=" << n_time_steps << endl;

  costs.resize(n_samples);
  
  // y_1..y_D  yd_1..yd_D  ydd_1..ydd_D  t=0
  // y_1..y_D  yd_1..yd_D  ydd_1..ydd_D  t=1
  //  |    |     |     |      |     |     |
  // y_1..y_D  yd_1..yd_D  ydd_1..ydd_D  t=T
  MatrixXd rollout; //(n_time_steps,n_cost_vars);
  MatrixXd my_row(1,n_time_steps*n_cost_vars);
  
  for (int k=0; k<n_samples; k++)
  {
    my_row = cost_vars.row(k);
    rollout = (Map<MatrixXd>(my_row.data(),n_cost_vars,n_time_steps)).transpose();   
    
    // rollout is of size   n_time_steps x n_cost_vars
    VectorXd ts = rollout.col(3 * n_dims);

    double dist_to_viapoint = 0.0;
    if (viapoint_weight_!=0.0)
    {
      if (viapoint_time_ == NO_VIAPOINT_TIME)
      {
        const MatrixXd y = rollout.block(0, 0, rollout.rows(), n_dims);
        dist_to_viapoint = (y.rowwise() - viapoint_.transpose()).rowwise().squaredNorm().minCoeff();
      }
      else
      {
        int viapoint_time_step = 0;
        while (viapoint_time_step < ts.size() && ts[viapoint_time_step] < viapoint_time_)
          viapoint_time_step++;

        assert(viapoint_time_step < ts.size());

        VectorXd y_via = rollout.row(viapoint_time_step).segment(0,n_dims);
        dist_to_viapoint = sqrt((y_via-viapoint_).array().pow(2).sum());
      }
    }
    
    double sum_ydd = 0.0;
    if (acceleration_weight_!=0.0)
    {
      MatrixXd ydd = rollout.block(0,2*n_dims,n_time_steps,n_dims);
      // ydd = n_time_steps x n_dims
      sum_ydd = ydd.array().pow(2).sum();
    }

    double delay_cost = 0.0;
    if (goal_weight_!=0.0)
    {
      int goal_time_step = 0;
      while (goal_time_step < ts.size() && ts[goal_time_step] < goal_time_)
        goal_time_step++;

      const MatrixXd y_after_goal = rollout.block(goal_time_step, 0,
        rollout.rows() - goal_time_step, n_dims);

      delay_cost = (y_after_goal.rowwise() - goal_.transpose()).rowwise().squaredNorm().sum();
    }

    costs[k] =  
      viapoint_weight_*dist_to_viapoint + 
      acceleration_weight_*sum_ydd/n_time_steps + 
      goal_weight_*delay_cost;
  }
}

void TaskViapoint::setCostFunctionWeighting(double viapoint_weight, double acceleration_weight, double goal_weight)
{
  viapoint_weight_      = viapoint_weight;
  acceleration_weight_  = acceleration_weight;
  goal_weight_          = goal_weight;            
}

void TaskViapoint::generateDemonstration(const MatrixXd& task_parameters, const VectorXd& ts, Trajectory& demonstration) const
{
  int n_dims = viapoint_.size();
  
  assert(task_parameters.rows()==1);
  assert(task_parameters.cols()==n_dims);	
	
	VectorXd y_from    = VectorXd::Constant(n_dims,0.0);
	VectorXd y_to      = VectorXd::Constant(n_dims,1.0);

	VectorXd y_yd_ydd_viapoint(3*n_dims);
	y_yd_ydd_viapoint << task_parameters.row(0), VectorXd::Constant(n_dims,1.0), VectorXd::Constant(n_dims,0.0);
  
  demonstration = Trajectory::generatePolynomialTrajectoryThroughViapoint(ts, y_from, y_yd_ydd_viapoint, viapoint_time_, y_to);

}

ostream& TaskViapoint::serialize(ostream& output) const {
  output << "TaskViapoint[";
  output << "viapoint=" << viapoint_.transpose();
  output << ", viapoint_time=" << viapoint_time_;
  output << "]";
  return output;
};

