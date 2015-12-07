#include <string>
#include <set>
#include <eigen3/Eigen/Core>

#include "dmp_bbo/runEvolutionaryOptimizationParallel.h"
#include "dmp_bbo/TaskViapoint.h"
#include "dmp_bbo/TaskViapointSolverDmp.h"

#include "dmp/Dmp.h"
#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/ModelParametersLWR.h"

#include "bbo/DistributionGaussian.h"
#include "bbo/Updater.h"
#include "bbo/updaters/UpdaterCovarDecay.h"

using namespace std;
using namespace Eigen;

int main(int n_args, char* args[])
{
  // If program has an argument, it is a directory to which to save files too (or --help)
  string directory;
  if (n_args>1)
  {
    if (string(args[1]).compare("--help")==0)
    {
      cout << "Usage: " << args[0] << " [directory]         (directory: optional directory to save data to)" << endl;
      return 0;
    }
    else
    {
      directory = string(args[1]);
    }
  }

  // Make the task
  int n_dim=2;
  
  VectorXd viapoint = VectorXd::LinSpaced(n_dim,1.5,2.0);
  double viapoint_time = 0.2;
  TaskViapoint* task = new TaskViapoint(viapoint,viapoint_time);
  
  // Some DMP parameters
  double tau = 0.6;
  VectorXd y_init = VectorXd::Constant(n_dim,1.0);
  VectorXd y_attr = VectorXd::Constant(n_dim,3.0);
 
  int n_basis_functions = 4;
  VectorXd centers = VectorXd::LinSpaced(n_basis_functions,0,1);
  VectorXd widths  = VectorXd::Constant(n_basis_functions,0.2);
  VectorXd slopes  = VectorXd::Zero(n_basis_functions);
  VectorXd offsets = VectorXd::Zero(n_basis_functions);
  ModelParametersLWR* model_parameters = new ModelParametersLWR(centers,widths,slopes,offsets);
  vector<FunctionApproximator*> function_approximators(n_dim);
  for (int i_dim=0; i_dim<n_dim; i_dim++)
    function_approximators[i_dim] = new FunctionApproximatorLWR(model_parameters);
  
  Dmp* dmp = new Dmp(tau, y_init, y_attr, function_approximators, Dmp::KULVICIUS_2012_JOINING);

  // Make the task solver
  set<string> parameters_to_optimize;
  parameters_to_optimize.insert("slopes");
  TaskViapointSolverDmp* task_solver = new TaskViapointSolverDmp(dmp,parameters_to_optimize);

  // Make the initial distribution
  vector<VectorXd> mean_init_vec;
  dmp->getModelParametersVectors(mean_init_vec);
  
  vector<DistributionGaussian*> distributions(n_dim);
  for (int i_dim=0; i_dim<n_dim; i_dim++)
  {
    cout << mean_init_vec[i_dim].transpose() << endl;
    VectorXd mean_init = mean_init_vec[i_dim];
  
    MatrixXd covar_init = 10000.0*MatrixXd::Identity(mean_init.size(),mean_init.size());
    
    distributions[i_dim] = new DistributionGaussian(mean_init,covar_init);
  }


  // Make the parameter updater
  double eliteness = 10;
  double covar_decay_factor = 0.8;
  string weighting_method("PI-BB");
  Updater* updater = new UpdaterCovarDecay(eliteness, covar_decay_factor, weighting_method);
  
  // Run the optimization
  int n_updates = 40;
  int n_samples_per_update = 15;
  runEvolutionaryOptimizationParallel(task, task_solver, distributions, updater, n_updates, n_samples_per_update,directory);
  
}