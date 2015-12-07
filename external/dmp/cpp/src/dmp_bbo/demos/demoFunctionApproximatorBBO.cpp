#include <string>
#include <set>
#include <eigen3/Eigen/Core>
#include <fstream>

#include "functionapproximators/FunctionApproximator.h"
#include "functionapproximators/MetaParametersLWR.h"
#include "functionapproximators/ModelParametersLWR.h"
#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/demos/targetFunction.hpp"

#include "bbo/DistributionGaussian.h"
#include "bbo/Updater.h"
#include "bbo/updaters/UpdaterCovarDecay.h"
#include "bbo/runEvolutionaryOptimization.h"
#include "bbo/Task.h"
#include "bbo/TaskSolver.h"

using namespace std;
using namespace Eigen;



class TaskApproximateFunction : public Task
{
public:
  TaskApproximateFunction(const VectorXd& inputs, const VectorXd& targets) 
  :
    inputs_(inputs),
    targets_(targets)
  {
  }
  
  void evaluate(const MatrixXd& cost_vars, const MatrixXd& task_parameters, VectorXd& costs) const
  {
    int n_samples = cost_vars.rows();
    costs.resize(n_samples);
    
    VectorXd predictions, diff_square;
    for (int k=0; k<n_samples; k++)
    {
      predictions = cost_vars.row(k);
      diff_square = (predictions.array()-targets_.array()).square();
      costs[k] = diff_square.mean();
    }
  }
  
  bool savePerformRolloutsPlotScript(string directory)
  {
    string filename = directory + "/plotRollouts.py";
    
    std::ofstream file;
    file.open(filename.c_str());
    if (!file.is_open())
    {
      std::cerr << "Couldn't open file '" << filename << "' for writing." << std::endl;
      return false;
    }
    
    
    file << "import numpy as np" << endl;
    file << "import matplotlib.pyplot as plt" << endl;
    file << "import sys, os" << endl;
    file << "def plotRollouts(cost_vars,ax):" << endl;
    file << "    inputs = [";
    file << fixed;
    for (int ii=0; ii<inputs_.size(); ii++)
    {
      if (ii>0) file << ", ";
      file << inputs_[ii];
    }
    file << "]" << endl;
    file << "    targets = [";
    for (int ii=0; ii<targets_.size(); ii++)
    {
      if (ii>0) file << ", ";
      file << targets_[ii];
    }
    file << "]" << endl;
    file << "    line_handles = ax.plot(inputs,cost_vars.T,linewidth=0.5)" << endl;
    file << "    ax.plot(inputs,targets,'-',color='k',linewidth=2)" << endl;
    file << "    return line_handles" << endl;
    file << "if __name__=='__main__':" << endl;
    file << "    # See if input directory was passed" << endl;
    file << "    if (len(sys.argv)==2):" << endl;
    file << "      directory = str(sys.argv[1])" << endl;
    file << "    else:" << endl;
    file << "      print 'Usage: '+sys.argv[0]+' <directory>';" << endl;
    file << "      sys.exit()" << endl;
    file << "    cost_vars = np.loadtxt(directory+\"cost_vars.txt\")" << endl;
    file << "    fig = plt.figure()" << endl;
    file << "    ax = fig.gca()" << endl;
    file << "    plotRollouts(cost_vars,ax)" << endl;
    file << "    plt.show()" << endl;
    
    file.close();
    
    return true;
  }

  ostream& serialize(ostream& output) const
  {
    output << "{ \"TaskApproximateFunctionSolver\": { \"inputs\":" << inputs_.transpose() << ", \"targets\":" << targets_.transpose() << "}"; // zzz Make JSON output
    return output;
  }
  
private:
  VectorXd inputs_;
  VectorXd targets_;
};






class TaskSolverApproximateFunction : public TaskSolver
{
public:
  TaskSolverApproximateFunction(FunctionApproximator* function_approximator, bool normalized, const MatrixXd& inputs)
  : 
    function_approximator_(function_approximator),
    normalized_(normalized),
    inputs_(inputs)
  {
  }
  
  void performRollouts(const MatrixXd& samples, const MatrixXd& task_parameters, MatrixXd& cost_vars) const
  {
    int n_samples = samples.rows();
    cost_vars.resize(n_samples,inputs_.size());
    
    VectorXd param_vector, targets, diff_square;
    MatrixXd predictions;
    for (int k=0; k<n_samples; k++)
    {
      param_vector = samples.row(k);
      function_approximator_->setParameterVectorSelected(param_vector, normalized_);
      function_approximator_->predict(inputs_,predictions);
      
      cost_vars.row(k) = predictions.transpose();
    }
  }
  
  
  ostream& serialize(ostream& output) const {
    output << "{ \"TaskSolverApproximateFunctionSolver\": { \"function_approximator\":" << *function_approximator_ << ", \"inputs\":" << inputs_.transpose() << ", \"targets\":" << inputs_.transpose() << "}"; // zzz Make JSON output
    return output;
  };
  
private:
  FunctionApproximator* function_approximator_;
  bool normalized_;
  const Eigen::MatrixXd inputs_;
};








int main(int n_args, char* args[])
{
  // If program has an argument, it is a directory to which to save files too (or --help)
  string directory;
  if (n_args!=2)
  {
    cout << "Usage: " << args[0] << " <directory>" << endl;
    return -1;
  }

  directory = string(args[1]);

  
  // Generate training data 
  int n_input_dims = 1;
  VectorXi n_samples_per_dim = VectorXi::Constant(1,40);
  if (n_input_dims==2) 
    n_samples_per_dim = VectorXi::Constant(2,25);
    
  MatrixXd inputs, targets, outputs;
  targetFunction(n_samples_per_dim,inputs,targets);
  
  // Locally Weighted Regression
  double overlap = 0.07;
  int n_rfs = 9;
  if (n_input_dims==2) n_rfs = 5;
  VectorXi num_rfs_per_dim = VectorXi::Constant(n_input_dims,n_rfs);
  MetaParametersLWR* meta_parameters_lwr = new MetaParametersLWR(n_input_dims,num_rfs_per_dim,overlap);
  FunctionApproximator* function_approximator = new FunctionApproximatorLWR(meta_parameters_lwr);

  cout << "Training of " << function_approximator->getName() << endl;
  function_approximator->train(inputs,targets,directory);
  
  // Make the task solver
  int n_targets = targets.rows();
  MatrixXd new_targets = targets.col(0).array() + VectorXd::LinSpaced(n_targets,-1.0,1.0).array().square();
  
  bool normalized = true;
  set<string> parameters_to_optimize;
  //parameters_to_optimize.insert("centers");
  //parameters_to_optimize.insert("widths");
  parameters_to_optimize.insert("offsets");
  parameters_to_optimize.insert("slopes");
  function_approximator->setSelectedParameters(parameters_to_optimize);
  
  TaskApproximateFunction* task = new TaskApproximateFunction(inputs,new_targets);
  
  TaskSolverApproximateFunction* task_solver = new TaskSolverApproximateFunction(function_approximator,normalized,inputs);

  // Make the initial distribution
  VectorXd mean_init;
  function_approximator->getParameterVectorSelected(mean_init,normalized);
 
  double std = 0.03;
  MatrixXd covar_init = std*std*MatrixXd::Identity(mean_init.size(),mean_init.size());

  DistributionGaussian* distribution = new DistributionGaussian(mean_init,covar_init);

  // Make the parameter updater
  double eliteness = 10;
  double covar_decay_factor = 0.9;
  string weighting_method("PI-BB");
  Updater* updater = new UpdaterCovarDecay(eliteness, covar_decay_factor, weighting_method);
  
  // Run the optimization
  int n_updates = 30;
  int n_samples_per_update = 10;
  bool overwrite = true;
  runEvolutionaryOptimization(task, task_solver, distribution, updater, n_updates, n_samples_per_update,directory,overwrite);
  
}