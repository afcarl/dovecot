/**
 * \file demoImitationAndOptimization.cpp
 * \author Freek Stulp
 * \brief  Demonstrates how to initialize a DMP, and then optimize it with an evolution strategy.
 *
 * \ingroup Demos
 * \ingroup Dmps
 * \ingroup EvolutionStrategies
 */
 
#include <string>
#include <set>
#include <fstream>
#include <eigen3/Eigen/Core>

#include "dmp_bbo/TaskViapoint.h"
#include "dmp_bbo/TaskViapointSolverDmp.h"

#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/MetaParametersLWR.h"

#include "dmp/Dmp.h"
#include "dmp/Trajectory.h"

#include "bbo/DistributionGaussian.h"
#include "bbo/Updater.h"
#include "bbo/updaters/UpdaterCovarDecay.h"
#include "bbo/updaters/UpdaterCovarAdaptation.h"
#include "dmp_bbo/runEvolutionaryOptimizationParallel.h"

using namespace std;
using namespace Eigen;

void runImitationAndOptimization(vector<FunctionApproximator*> function_approximators, const Trajectory& trajectory, Task* task, Updater* updater, string directory)
{

  // Initialize and train DMP  
  int n_dims_dmp = trajectory.dim();
  Dmp* dmp = new Dmp(n_dims_dmp, function_approximators, Dmp::KULVICIUS_2012_JOINING);
  dmp->train(trajectory);
  
  // Integrate the trained DMP analytically   
  Trajectory trajectory_repro;
  dmp->analyticalSolution(trajectory.ts(),trajectory_repro);
  
  // Make the task solver
  set<string> parameters_to_optimize;
  parameters_to_optimize.insert("slopes");
  TaskViapointSolverDmp* task_solver = new TaskViapointSolverDmp(dmp,parameters_to_optimize);

  // Make the initial distribution
  vector<VectorXd> mean_init_vec;
  dmp->getModelParametersVectors(mean_init_vec);
  
  int n_dims = dmp->dim_orig();
  vector<DistributionGaussian*> distributions(n_dims);
  for (int i_dim=0; i_dim<n_dims; i_dim++)
  {
    cout << mean_init_vec[i_dim].transpose() << endl;
    VectorXd mean_init = mean_init_vec[i_dim];
  
    MatrixXd covar_init = 1000.0*MatrixXd::Identity(mean_init.size(),mean_init.size());
    
    distributions[i_dim] = new DistributionGaussian(mean_init,covar_init);
  }
  
  // Run the optimization
  int n_updates = 50;
  int n_samples_per_update = 15;
  
  runEvolutionaryOptimizationParallel(task, task_solver, distributions, updater, n_updates, n_samples_per_update,directory);
  
  // Save the initial data (doing this after runEvolutionaryOptimization so that it can take care of
  // checking/making the directory)
  if (!directory.empty())
  {
    std::ofstream outfile;
    
    outfile.open((directory+"traj_demo.txt").c_str()); 
    outfile << trajectory; 
    outfile.close();
    
    outfile.open((directory+"traj_repro.txt").c_str()); 
    outfile << trajectory_repro; 
    outfile.close();
  }
  

}

int main(int n_args, char* args[])
{
  string directory;
  if (n_args>1)
    directory = string(args[1]);
  
  // Generate a minimum-jerk trajectory for training
  int n_dims = 2;
  int n_time_steps = 51;
  VectorXd ts = VectorXd::LinSpaced(n_time_steps,0,0.5  );
  VectorXd y_first(n_dims); y_first << 0.0,0.1;
  VectorXd y_last(n_dims);  y_last  << 1.0,0.9;
  Trajectory traj_demo = Trajectory::generateMinJerkTrajectory(ts, y_first, y_last);
  
  // Make some LWR function approximators
  int n_basis_functions = 21;
  double overlap = 0.03;
  int n_input_dims = 1; // Each function approximator only takes phase as input
  MetaParametersLWR* meta_parameters = new MetaParametersLWR(n_input_dims,n_basis_functions,overlap);      
  vector<FunctionApproximator*> function_approximators(n_dims);    
  for (int dd=0; dd<n_dims; dd++)
    function_approximators[dd] = new FunctionApproximatorLWR(meta_parameters);
  
  // Make the task to be solved
  VectorXd viapoint = VectorXd::LinSpaced(n_dims,0.3,0.7);
  double viapoint_time = 0.5*traj_demo.duration();
  Task* task = new TaskViapoint(viapoint,viapoint_time);
  
  // Make the parameter updater
  double eliteness = 10;
  double covar_decay_factor = 0.9;
  string weighting_method("PI-BB");
  Updater* updater = new UpdaterCovarDecay(eliteness, covar_decay_factor, weighting_method);

  VectorXd base_level = VectorXd::Constant(n_basis_functions,5.0);
  eliteness = 10;
  bool diag_only = false;
  double learning_rate = 0.5;
  updater = new UpdaterCovarAdaptation(eliteness,weighting_method,base_level,diag_only,learning_rate);  
  

  // Calls function at the top of this file
  runImitationAndOptimization(function_approximators, traj_demo, task, updater, directory);
  
  
}