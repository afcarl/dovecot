#include "dmp/Dmp.h"
#include "dmp/DmpContextualTwoStep.h"

#include "dmp/Trajectory.h"
#include "functionapproximators/FunctionApproximator.h"
#include "functionapproximators/FunctionApproximatorLWR.h"

#include <iostream>
#include <eigen3/Eigen/Core>
#include <boost/lexical_cast.hpp>

using namespace std;
using namespace Eigen;

DmpContextualTwoStep::DmpContextualTwoStep(int n_dims_dmp, vector<FunctionApproximator*> function_approximators, FunctionApproximator* policy_parameter_function, DmpType dmp_type) 
:  DmpContextual(n_dims_dmp, function_approximators, dmp_type)
{
  policy_parameter_function_ = vector<vector<FunctionApproximator*> >(dim_orig());
  for (int dd=0; dd<dim_orig(); dd++)
  { 
    policy_parameter_function_[dd] = vector<FunctionApproximator*>(1);
    policy_parameter_function_[dd][0] = policy_parameter_function->clone();
  }
}

// Overloads in DMP computeFunctionApproximatorOutput
void DmpContextualTwoStep::computeFunctionApproximatorOutput(const MatrixXd& phase_state, MatrixXd& fa_output) const
{
  int n_time_steps = phase_state.rows(); 
  fa_output.resize(n_time_steps,dim_orig());
  fa_output.fill(0.0);
  
  if (task_parameters_.rows()==0)
  {
    // When the task parameters are not set, we cannot compute the output of the function approximator.
    return;
  }
  
  MatrixXd task_parameters = task_parameters_;
  if (task_parameters.rows()==1)
  { 
    task_parameters = task_parameters.row(0).replicate(n_time_steps,1).eval();
  }
  else if (task_parameters.cols()==1)
  {
    task_parameters = task_parameters.col(0).transpose().replicate(n_time_steps,1).eval();
  }

  assert(n_time_steps==task_parameters.rows());
  
  //int n_task_parameters = task_parameters.cols();
  
  VectorXd model_parameters;
  MatrixXd output(1,1);
  for (int dd=0; dd<dim_orig(); dd++)
  { 
    int n_parameters = function_approximator(dd)->getParameterVectorSelectedSize();
    model_parameters.resize(n_parameters);
    for (int pp=0; pp<n_parameters; pp++)
    {
      policy_parameter_function_[dd][pp]->predict(task_parameters,output);
      model_parameters[pp] = output(0,0);
    }
    function_approximator(dd)->setParameterVectorSelected(model_parameters);
  }

  // The parameters of the function_approximators have been set, get their outputs now.  
  for (int dd=0; dd<dim_orig(); dd++)
  {
    function_approximator(dd)->predict(phase_state,output);
    if (output.size()>0)
    {
      fa_output.col(dd) = output;
    }
  }

}

bool DmpContextualTwoStep::isTrained(void) const
{
  for (int dd=0; dd<dim_orig(); dd++)
    for (unsigned int pp=0; pp<policy_parameter_function_[dd].size(); pp++)
      if (!policy_parameter_function_[dd][pp]->isTrained())
        return false;
      
  return true;   
}

void  DmpContextualTwoStep::train(const vector<Trajectory>& trajectories, const vector<MatrixXd>& task_parameters, string save_directory)
{
  // Check if inputs are of the right size.
  unsigned int n_demonstrations = trajectories.size();
  assert(n_demonstrations==task_parameters.size());  
  
  
  // Then check if the trajectories have the same duration and initial/final state
  // Later on, if they are not the same, they should be learned also.
  checkTrainTrajectories(trajectories);

  // Set tau, initial_state and attractor_state from the trajectories 
  set_tau(trajectories[0].duration());
  set_initial_state(trajectories[0].initial_y());
  set_attractor_state(trajectories[0].final_y());

  MatrixXd cur_task_parameters;
  VectorXd cur_model_parameters;// zzz Remove redundant tmp variable
  vector<MatrixXd> all_model_parameters(n_demonstrations); 
  for (unsigned int i_demo=0; i_demo<n_demonstrations; i_demo++)
  {
    
    string save_directory_demo;
    if (!save_directory.empty())
      save_directory_demo = save_directory + "/demo" + boost::lexical_cast<string>(i_demo);
    
    bool overwrite = true; // zzz Should be argument of function
    Dmp::train(trajectories[i_demo],save_directory_demo,overwrite);
    
    for (int i_dim=0; i_dim<dim_orig(); i_dim++)
    {
      function_approximator(i_dim)->setSelectedParametersOne(string("slopes")); // zzz Should be argument of constructor
  
      function_approximator(i_dim)->getParameterVectorSelected(cur_model_parameters);
      //cout << cur_model_parameters << endl;
      if (i_demo==0)
        all_model_parameters[i_dim].resize(n_demonstrations,cur_model_parameters.size());
      else
        assert(cur_model_parameters.size()==all_model_parameters[i_dim].cols());

      all_model_parameters[i_dim].row(i_demo) = cur_model_parameters;
      
    }
  }

   
  // Gather task parameters in a matrix
  int n_task_parameters = task_parameters[0].cols();
  // This is the first time task_parameters_ is set, because this is the first time we know 
  // n_task_parameters.
  // We set it so that set_task_parameters can check if task_parameters_.cols()==n_task_parameters
  task_parameters_ = MatrixXd::Zero(1,n_task_parameters);
  
  MatrixXd inputs(n_demonstrations,n_task_parameters);
  for (unsigned int i_demo=0; i_demo<n_demonstrations; i_demo++)
  {
    if (task_parameters[i_demo].rows()>0)
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "WARNING. For DmpContextualTwoStep, task parameters may not vary over time during training. Using task parameters at t=0 only." << endl;
    }
    inputs.row(i_demo) = task_parameters[i_demo].row(0);
  }

  
  // Input to policy parameter functions: task_parameters
  // Target for each policy parameter function: all_model_parameters.col(param)
  
  for (int i_dim=0; i_dim<dim_orig(); i_dim++)
  {
    int n_pol_pars = all_model_parameters[i_dim].cols();
    for (int i_pol_par=1; i_pol_par<n_pol_pars; i_pol_par++)
    {
      policy_parameter_function_[i_dim].push_back(policy_parameter_function_[i_dim][0]->clone());
      //cout << *(policy_parameter_function_[i_dim][i_pol_par]) << endl;
    }

    for (int i_pol_par=0; i_pol_par<n_pol_pars; i_pol_par++)
    {
      MatrixXd targets = all_model_parameters[i_dim].col(i_pol_par);
      //cout << "_________________" << endl;
      //cout << inputs.transpose() << endl << endl;
      //cout << targets.transpose() << endl;
      
      string save_directory_cur;
      if (!save_directory.empty())
          save_directory_cur = save_directory + "/dim" + boost::lexical_cast<string>(i_dim) + "_polpar" + boost::lexical_cast<string>(i_pol_par);
      
      bool overwrite = true; // zzz
      policy_parameter_function_[i_dim][i_pol_par]->train(inputs,targets,save_directory_cur,overwrite);
    
    }
  }
  
  
}

