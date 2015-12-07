#include "bbo/runEvolutionaryOptimization.h"

#include "bbo/DistributionGaussian.h"
#include "bbo/Updater.h"
#include "bbo/UpdateSummary.h"
#include "bbo/CostFunction.h"
#include "bbo/Task.h"
#include "bbo/TaskSolver.h"
#include "utilities/EigenFileIO.hpp"

#include <iomanip>
#include <fstream>
#include <boost/filesystem.hpp>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

void runEvolutionaryOptimization(CostFunction* cost_function, DistributionGaussian* distribution, Updater* updater, int n_updates, int n_samples_per_update, string save_directory, bool overwrite)
{
  //if (!saveCostFunction(save_directory, cost_function, overwrite)) nnn fix this
  //  return;

  // Some variables
  MatrixXd samples;
  VectorXd costs, cost_eval;
  UpdateSummary update_summary;
  
  // Optimization loop
  if (save_directory.empty()) 
    cout << "init  =  " << "  distribution=" << *distribution << endl;
  for (int i_update=1; i_update<=n_updates; i_update++)
  {
    // 0. Get cost of current distribution mean
    cost_function->evaluate(distribution->mean().transpose(),cost_eval);
    update_summary.cost_eval = cost_eval[0];
    
    // 1. Sample from distribution
    distribution->generateSamples(n_samples_per_update, samples);

    // 2. Evaluate the samples
    cost_function->evaluate(samples,costs);
  
    // 3. Update parameters
    updater->updateDistribution(*distribution, samples, costs, *distribution, update_summary);
      
    // Some output and/or saving to file (if "directory" is set)
    if (save_directory.empty()) 
    {
      cout << "update=" << i_update << " cost_eval=" << update_summary.cost_eval << "    " << *distribution << endl;
    }
    else
    {
      cout << i_update << " ";
      stringstream stream;
      stream << save_directory << "/update" << setw(5) << setfill('0') << i_update << "/";
      saveToDirectory(update_summary, stream.str());
    }
  
  }
  cout << endl;
}

// This function could have been integrated with the above. But I preferred to duplicate a bit of
// code so that the difference between running an optimziation with a CostFunction or
// Task/TaskSolver is more apparent.
void runEvolutionaryOptimization(Task* task, TaskSolver* task_solver, DistributionGaussian* distribution, Updater* updater, int n_updates, int n_samples_per_update, string save_directory, bool overwrite)
{
  //if (!saveCostFunction(save_directory, cost_function, overwrite)) nnn fix this
  //  return;

  // Some variables
  MatrixXd samples;
  MatrixXd cost_vars, cost_vars_eval;
  VectorXd costs, cost_eval;
  UpdateSummary update_summary;
  
  // Optimization loop
  if (save_directory.empty()) 
    cout << "init  =  " << "  distribution=" << *distribution << endl;
  for (int i_update=1; i_update<=n_updates; i_update++)
  {
    // 0. Get cost of current distribution mean
    task_solver->performRollouts(distribution->mean().transpose(),cost_vars_eval);
    task->evaluate(cost_vars_eval,cost_eval);
    update_summary.cost_eval = cost_eval[0];
    
    // 1. Sample from distribution
    distribution->generateSamples(n_samples_per_update, samples);

    // 2A. Perform the roll-outs
    task_solver->performRollouts(samples,cost_vars);
  
    // 2B. Evaluate the samples
    task->evaluate(cost_vars,costs);
  
    // 3. Update parameters
    updater->updateDistribution(*distribution, samples, costs, *distribution, update_summary);
      
    // Some output and/or saving to file (if "directory" is set)
    if (save_directory.empty()) 
    {
      cout << "update=" << i_update << " cost_eval=" << update_summary.cost_eval << "    " << *distribution << endl;
    }
    else
    {
      cout << i_update << " ";
      stringstream stream;
      stream << save_directory << "/update" << setw(5) << setfill('0') << i_update << "/";
      saveToDirectory(update_summary, stream.str());
      
      bool overwrite = true;
      saveMatrix(stream.str(),"cost_vars.txt",cost_vars,overwrite);
      saveMatrix(stream.str(),"cost_vars_eval.txt",cost_vars_eval,overwrite);
      
      task->savePerformRolloutsPlotScript(save_directory);

    }
  
  }
  cout << endl;
}
