#include "dmp/DmpContextual.h"

#include "dmp/Trajectory.h"

#include <iostream>
#include <eigen3/Eigen/Core>


using namespace std;
using namespace Eigen;

DmpContextual::DmpContextual(int n_dims_dmp, vector<FunctionApproximator*> function_approximators, DmpType dmp_type) 
:  Dmp(n_dims_dmp, function_approximators, dmp_type)
{
   
}


void  DmpContextual::train(const vector<Trajectory>& trajectories, const vector<MatrixXd>& task_parameters)
{
  train(trajectories, task_parameters, string(""));
}

void  DmpContextual::train(const vector<Trajectory>& trajectories)
{
  train(trajectories, string(""));
}

void  DmpContextual::train(const vector<Trajectory>& trajectories, string save_directory)
{
  vector<MatrixXd> task_parameters(trajectories.size());
  for (unsigned int i_traj=0; i_traj<trajectories.size(); i_traj++)
  {
    task_parameters[i_traj] = trajectories[i_traj].misc();
    assert(task_parameters[i_traj].cols()>0);
    if (i_traj>0)
      assert(task_parameters[i_traj].cols() ==  task_parameters[i_traj].cols());
  }
  train(trajectories, task_parameters, save_directory);
}


void  DmpContextual::checkTrainTrajectories(const vector<Trajectory>& trajectories)
{
  // Check if inputs are of the right size.
  unsigned int n_demonstrations = trajectories.size();
  
  // Then check if the trajectories have the same duration and initial/final state
  double first_duration = trajectories[0].duration();
  VectorXd first_y_init = trajectories[0].initial_y();
  VectorXd first_y_attr = trajectories[0].final_y();  
  for (unsigned int i_demo=1; i_demo<n_demonstrations; i_demo++)
  {
    // Difference in tau
    if (fabs(first_duration-trajectories[i_demo].duration())>10e-4)
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "WARNING: Duration of demonstrations differ (" << first_duration << "!=" << trajectories[i_demo].duration() << ")" << endl;
    }
    
    // Difference between initial states
    double sum_abs_diff = (first_y_init.array()-trajectories[i_demo].initial_y().array()).abs().sum();
    if (sum_abs_diff>10e-7)
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "WARNING: Final states of demonstrations differ ( [" << first_y_init.transpose() << "] != [ " << trajectories[i_demo].initial_y().transpose() << "] )" << endl;
    }
    
    // Difference between final states
    sum_abs_diff = (first_y_attr.array()-trajectories[i_demo].final_y().array()).abs().sum();
    if (sum_abs_diff>10e-7)
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "WARNING: Final states of demonstrations differ ( [" << first_y_attr.transpose() << "] != [ " << trajectories[i_demo].final_y().transpose() << "] )" << endl;
    }
    
  }
}

