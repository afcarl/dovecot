/**
 * \file demoEvolutionaryOptimizationTask.cpp
 * \author Freek Stulp
 * \brief  Demonstrates how to run an evolution strategy to optimize the parameters of a quadratic function, implemented as a Task and TaskSolver.
 *
 * \ingroup Demos
 * \ingroup BBO
 */

#include "bbo/Task.h"
#include "bbo/TaskSolver.h"
#include "bbo/runEvolutionaryOptimization.h"
#include "bbo/DistributionGaussian.h"

#include "bbo/updaters/UpdaterMean.h"
#include "bbo/updaters/UpdaterCovarDecay.h"
#include "bbo/updaters/UpdaterCovarAdaptation.h"

#include <iomanip> 
#include <fstream> 
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

/** Target function \f$ y = a*x^2 + c \f$
 *  \param[in] a a in \f$ y = a*x^2 + c \f$
 *  \param[in] c c in \f$ y = a*x^2 + c \f$
 *  \param[in] inputs x in \f$ y = a*x^2 + c \f$
 *  \param[out] outputs y in \f$ y = a*x^2 + c \f$
 */
void targetFunction(double a, double c, const VectorXd& inputs, VectorXd& outputs)
{
  // Compute a*x^2 + c
  outputs =  (a*inputs).array().square() + c;
}

/**
 * The task is to choose the parameters a and c such that the function \f$ y = a*x^2 + c \f$ best matches a set of target values y_target for a set of input values x
 */
class TaskApproximateQuadraticFunction : public Task
{
public:
  /** Constructor
   *  \param[in] a a in \f$ y = a*x^2 + c \f$
   *  \param[in] c c in \f$ y = a*x^2 + c \f$
   *  \param[in] inputs x in \f$ y = a*x^2 + c \f$
   */
  TaskApproximateQuadraticFunction(double a, double c, const VectorXd& inputs) 
  {
    inputs_ = inputs;
    targetFunction(a,c,inputs_,targets_);
  }
  
  /** Cost function
   * \param[in] cost_vars y in \f$ y = a*x^2 + c \f$
   * \param[in] task_parameters Ignored
   * \param[out] costs Costs of the cost_vars
   */
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
  
  /** Save a python script that is able to visualize the rollouts, given the cost-relevant variables
   *  stored in a file.
   *  \param[in] directory Directory in which to save the python script
   *  \return true if saving the script was successful, false otherwise
   */
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
    file << "    ax.plot(inputs,targets,'-o',color='k',linewidth=2)" << endl;
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

  /** Write object to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output stream to which the object was written 
   */
  ostream& serialize(ostream& output) const
  {
    output << "{ \"TaskApproximateQuadraticFunctionSolver\": { \"inputs\":" << inputs_.transpose() << ", \"targets\":" << targets_.transpose() << "}"; // zzz Make JSON output
    return output;
  }
  
private:
  VectorXd inputs_;
  VectorXd targets_;
};


/** The task solver tunes the parameters a and c such that the function \f$ y = a*x^2 + c \f$ best matches a set of target values y_target for a set of input values x
 */
class TaskSolverApproximateQuadraticFunction : public TaskSolver
{
public:
  /**
   *  \param[in] inputs x in \f$ y = a*x^2 + c \f$
   */
  TaskSolverApproximateQuadraticFunction(const VectorXd& inputs) 
  {
    inputs_ = inputs;
  }
  
  /** Cost function
   * \param[in] samples Samples containing variations of a and c  (in  \f$ y = a*x^2 + c \f$)
   * \param[in] task_parameters Ignored
   * \param[in] cost_vars Cost-relevant variables, containing the predictions
   */
  void performRollouts(const MatrixXd& samples, const MatrixXd& task_parameters, MatrixXd& cost_vars) const 
  {
    int n_samples = samples.rows();
    cost_vars.resize(n_samples,inputs_.size());
    
    VectorXd predictions, diff_square;
    for (int k=0; k<n_samples; k++)
    {
      double a = samples(k,0);
      double c = samples(k,1);
      targetFunction(a,c,inputs_,predictions);
      
      cost_vars.row(k) = predictions;
    }
  }
  
  /** Write object to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output stream to which the object was written 
   */
  ostream& serialize(ostream& output) const
  {
    output << "{ \"TaskApproximateQuadraticFunctionSolver\": { \"inputs\":" << inputs_.transpose() << "}"; // zzz Make JSON output
    return output;
  }
  
private:
  VectorXd inputs_;
};




/** Main function
 * \param[in] n_args Number of arguments
 * \param[in] args Arguments themselves
 * \return Success of exection. 0 if successful.
 */
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
  
  VectorXd inputs = VectorXd::LinSpaced(21,-1.5,1.5);
  double a = 2.0;
  double c = -1.0;
  int n_params = 2;
  
  Task* task = new TaskApproximateQuadraticFunction(a,c,inputs);
  TaskSolver* task_solver = new TaskSolverApproximateQuadraticFunction(inputs); 
  
  VectorXd mean_init  =  0.5*VectorXd::Ones(n_params);
  MatrixXd covar_init =  0.2*MatrixXd::Identity(n_params,n_params);
  DistributionGaussian* distribution = new DistributionGaussian(mean_init, covar_init); 
  
  Updater* updater = NULL;
  double eliteness = 10;
  string weighting_method = "PI-BB";
    
  if (false)
  {
    updater = new UpdaterMean(eliteness,weighting_method);
  }
  
  if (false)
  {
    double covar_decay_factor = 0.8;
    updater = new UpdaterCovarDecay(eliteness,covar_decay_factor,weighting_method);
  }
  
  if (updater==NULL)
  {
    VectorXd base_level = VectorXd::Constant(n_params,0.000001);
    bool diag_only = false;
    double learning_rate = 0.5;
    updater = new UpdaterCovarAdaptation(eliteness,weighting_method,base_level,diag_only,learning_rate);  
  }
    
  
  int n_samples_per_update = 10;
  
  int n_updates = 20;
  
  runEvolutionaryOptimization(task, task_solver, distribution, updater, n_updates, n_samples_per_update,directory);
  
  return 0;
}


