#include "dmp/Dmp.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <string>
#include <eigen3/Eigen/Core>
#include <boost/lexical_cast.hpp>

#include "dmp/Trajectory.h"
#include "functionapproximators/FunctionApproximator.h"
#include "dynamicalsystems/SpringDamperSystem.h"
#include "dynamicalsystems/ExponentialSystem.h"
#include "dynamicalsystems/TimeSystem.h"
#include "dynamicalsystems/SigmoidSystem.h"

#include "dynamicalsystems/deserializeDynamicalSystem.h"
#include "utilities/EigenJSON.hpp"
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>


using namespace std;
using namespace Eigen;

#define SPRING    segment(0*dim_orig()+0,2*dim_orig())
#define SPRING_Y  segment(0*dim_orig()+0,dim_orig())
#define SPRING_Z  segment(1*dim_orig()+0,dim_orig())
#define GOAL      segment(2*dim_orig()+0,dim_orig())
#define PHASE     segment(3*dim_orig()+0,       1)
#define GATING    segment(3*dim_orig()+1,       1)

#define SPRINGM(T)    block(0,0*dim_orig()+0,T,2*dim_orig())
#define SPRINGM_Y(T)  block(0,0*dim_orig()+0,T,dim_orig())
#define SPRINGM_Z(T)  block(0,1*dim_orig()+0,T,dim_orig())
#define GOALM(T)      block(0,2*dim_orig()+0,T,dim_orig())
#define PHASEM(T)     block(0,3*dim_orig()+0,T,       1)
#define GATINGM(T)    block(0,3*dim_orig()+1,T,       1)

Dmp::Dmp(double tau, VectorXd y_init, VectorXd y_attr, 
         vector<FunctionApproximator*> function_approximators,
         double alpha_spring_damper, 
         DynamicalSystem* goal_system,
         DynamicalSystem* phase_system, 
         DynamicalSystem* gating_system)
  : DynamicalSystem(1, tau, y_init, y_attr, "name"),
  goal_system_(goal_system),
  phase_system_(phase_system), gating_system_(gating_system) 
{
  initSubSystems(alpha_spring_damper, goal_system, phase_system, gating_system);
  initFunctionApproximators(function_approximators);
}

  
Dmp::Dmp(int n_dims_dmp, vector<FunctionApproximator*> function_approximators, 
   double alpha_spring_damper, DynamicalSystem* goal_system,
   DynamicalSystem* phase_system, DynamicalSystem* gating_system)
  : DynamicalSystem(1, 1.0, VectorXd::Zero(n_dims_dmp), VectorXd::Ones(n_dims_dmp), "name"),
  goal_system_(goal_system),
  phase_system_(phase_system), gating_system_(gating_system), function_approximators_(function_approximators)
{
  initSubSystems(alpha_spring_damper, goal_system, phase_system, gating_system);
  initFunctionApproximators(function_approximators);
}
    
Dmp::Dmp(double tau, VectorXd y_init, VectorXd y_attr, 
         vector<FunctionApproximator*> function_approximators, 
         DmpType dmp_type)
  : DynamicalSystem(1, tau, y_init, y_attr, "name")
{  
  initSubSystems(dmp_type);
  initFunctionApproximators(function_approximators);
}
  
Dmp::Dmp(int n_dims_dmp, 
         vector<FunctionApproximator*> function_approximators, 
         DmpType dmp_type)
  : DynamicalSystem(1, 1.0, VectorXd::Zero(n_dims_dmp), VectorXd::Ones(n_dims_dmp), "name")
{
  initSubSystems(dmp_type);
  initFunctionApproximators(function_approximators);
}

void Dmp::initSubSystems(DmpType dmp_type)
{
  VectorXd one_1 = VectorXd::Ones(1);
  VectorXd one_0 = VectorXd::Zero(1);
  
  DynamicalSystem *goal_system=NULL;
  DynamicalSystem *phase_system=NULL;
  DynamicalSystem *gating_system=NULL;
  if (dmp_type==IJSPEERT_2002_MOVEMENT)
  {
    goal_system   = NULL;
    phase_system  = new ExponentialSystem(tau(),one_1,one_0,4);
    gating_system = new ExponentialSystem(tau(),one_1,one_0,4); 
  }                                                          
  else if (dmp_type==KULVICIUS_2012_JOINING)
  {
    goal_system   = new ExponentialSystem(tau(),initial_state(),attractor_state(),15);
    phase_system  = new TimeSystem(tau());
    gating_system = new SigmoidSystem(tau(),one_1,-40,0.9*tau()); 
  }
  
  double alpha_spring_damper = 20;
  
  initSubSystems(alpha_spring_damper, goal_system, phase_system, gating_system);
}

void Dmp::initSubSystems(double alpha_spring_damper, DynamicalSystem* goal_system,
  DynamicalSystem* phase_system, DynamicalSystem* gating_system)
{
  

  // Make room for the subsystems
  set_dim(3*dim_orig()+2);
    
  spring_system_ = new SpringDamperSystem(tau(),initial_state(),attractor_state(),alpha_spring_damper);  
  spring_system_->set_name(name()+"_spring-damper");

  if (goal_system!=NULL)
  {
    goal_system_ = goal_system;
    // Initial state of the goal system is that same as that of the DMP
    goal_system_->set_initial_state(initial_state());
    goal_system_->set_name(name()+"_goal");
  }

  phase_system_ = phase_system;
  phase_system_->set_name(name()+"_phase");

  gating_system_ = gating_system;
  gating_system_->set_name(name()+"_gating");

}

void Dmp::initFunctionApproximators(vector<FunctionApproximator*> function_approximators)
{
  if (function_approximators.empty())
    return;
  
  assert(dim_orig()==(int)function_approximators.size());
  
  function_approximators_ = vector<FunctionApproximator*>(function_approximators.size());
  for (unsigned int dd=0; dd<function_approximators.size(); dd++)
  {
    if (function_approximators[dd]==NULL)
      function_approximators_[dd] = NULL;
    else
      function_approximators_[dd] = function_approximators[dd]->clone();
  }

}

Dmp::~Dmp(void)
{
  delete goal_system_;   
  delete spring_system_;
  delete phase_system_;
  delete gating_system_;
  for (unsigned int ff=0; ff<function_approximators_.size(); ff++)
    delete (function_approximators_[ff]);
}

Dmp* Dmp::clone(void) const {
  vector<FunctionApproximator*> function_approximators;
  for (unsigned int ff=0; ff<function_approximators_.size(); ff++)
    function_approximators.push_back(function_approximators_[ff]->clone());
  
  return new Dmp(tau(), initial_state(), attractor_state(), function_approximators,
   spring_system_->damping_coefficient(), goal_system_->clone(),
   phase_system_->clone(), gating_system_->clone());
}


void Dmp::integrateStart(Ref<VectorXd> x, Ref<VectorXd> xd) const
{
  assert(x.size()==dim());
  assert(xd.size()==dim());
  
  x.fill(0);  
  xd.fill(0);  
  
  // Start integrating goal system if it exists
  if (goal_system_==NULL)
  {
    // No goal system, simply set goal state to attractor state
    x.GOAL = attractor_state();
    xd.GOAL.fill(0);
  }
  else
  {
    // Goal system exists. Start integrating it.
    goal_system_->integrateStart(x.GOAL,xd.GOAL);
  }
  
    
  // Set the attractor state of the spring system
  spring_system_->set_attractor_state(x.GOAL);
  
  // Start integrating all futher subsystems
  spring_system_->integrateStart(x.SPRING, xd.SPRING);
  phase_system_->integrateStart(  x.PHASE,  xd.PHASE);
  gating_system_->integrateStart(x.GATING, xd.GATING);

  // Add rates of change
  differentialEquation(x,xd);
  
}

/*
bool Dmp::isTrained(void) const
{
  for (int i_dim=0; i_dim<dim_orig(); i_dim++)
    if (function_approximators_[i_dim]!=NULL)
      return false;
    
  for (int i_dim=0; i_dim<dim_orig(); i_dim++)
    if (function_approximators_[i_dim]->isTrained()) 
      return false;
    
  return true;
}
*/

void Dmp::computeFunctionApproximatorOutput(const MatrixXd& phase_state, MatrixXd& fa_output) const
{
  int T = phase_state.rows();
  fa_output.resize(T,dim_orig());
  fa_output.fill(0.0);
  
  MatrixXd output(T,1);
  for (int i_dim=0; i_dim<dim_orig(); i_dim++)
  {
    if (function_approximators_[i_dim]!=NULL)
    {
      if (function_approximators_[i_dim]->isTrained()) 
      {
        function_approximators_[i_dim]->predict(phase_state,output);
        fa_output.col(i_dim) = output;
      }
    }
  }
}

void Dmp::differentialEquation(const VectorXd& x, Ref<VectorXd> xd) const
{
  
  if (goal_system_==NULL)
  {
    // If there is no dynamical system for the delayed goal, the goal is
    // simply the attractor state
    spring_system_->set_attractor_state(attractor_state());
    // with zero change
    xd.GOAL.fill(0);
  } 
  else
  {
    // Integrate goal system and get current goal state
    goal_system_->set_attractor_state(attractor_state());
    goal_system_->differentialEquation(x.GOAL, xd.GOAL);
    // The goal state is the attractor state of the spring-damper system
    spring_system_->set_attractor_state(x.GOAL);
        
  }

  // Integrate spring damper system
  // Forcing term is added to spring_state later
  spring_system_->differentialEquation(x.SPRING, xd.SPRING);

  
  // Non-linear forcing term
  phase_system_->differentialEquation(x.PHASE, xd.PHASE);
  gating_system_->differentialEquation(x.GATING, xd.GATING);

  MatrixXd phase_state(1,1);
  phase_state = x.PHASE;
  MatrixXd fa_output(1,dim_orig());
  computeFunctionApproximatorOutput(phase_state, fa_output); 
  
  int t0 = 0;
  double gating = (x.GATING)[0];
  VectorXd g_minus_y0 = (attractor_state()-initial_state()).transpose();
  VectorXd forcing_term = gating*fa_output.row(t0); // zzz .array()*g_minus_y0.array();

  // Add forcing term to the ZD component of the spring state
  xd.SPRING_Z = xd.SPRING_Z + forcing_term/tau();


}


void Dmp::statesAsTrajectory(const MatrixXd& x_in, const MatrixXd& xd_in, MatrixXd& y_out, MatrixXd& yd_out, MatrixXd& ydd_out) const
{
  int n_time_steps = x_in.rows(); 
  y_out  = x_in.SPRINGM_Y(n_time_steps);
  yd_out = xd_in.SPRINGM_Y(n_time_steps);
  ydd_out = xd_in.SPRINGM_Z(n_time_steps)/tau();
  // MatrixXd z_out, zd_out;
  // z_out  = x_in.SPRINGM_Z(n_time_steps);
  // zd_out = xd_in.SPRINGM_Z(n_time_steps);
  // Divide by tau to go from z to y space
  // yd = z_out/obj.tau;
  // ydd_out = zd_out/tau();
}


void Dmp::statesAsTrajectory(const VectorXd& ts, const MatrixXd& x_in, const MatrixXd& xd_in, Trajectory& trajectory) const {
  int n_time_steps = ts.rows();
  int n_dims       = x_in.cols();
  assert(n_time_steps==x_in.rows());
  assert(n_time_steps==xd_in.rows());
  assert(n_dims==xd_in.cols());

  // Left column is time
  Trajectory new_trajectory(
    ts,
    // y_out (see function above)
    x_in.SPRINGM_Y(n_time_steps),
    // yd_out (see function above)
    xd_in.SPRINGM_Y(n_time_steps),
    // ydd_out (see function above)
    xd_in.SPRINGM_Z(n_time_steps)/tau()
  );
  
  trajectory = new_trajectory;
  
}

void Dmp::analyticalSolution(const VectorXd& ts, MatrixXd& xs, MatrixXd& xds, Eigen::MatrixXd& forcing_terms, Eigen::MatrixXd& fa_outputs) const
{
  int n_time_steps = ts.size();
  
  // INTEGRATE SYSTEMS ANALYTICALLY AS MUCH AS POSSIBLE

  // Integrate phase
  MatrixXd xs_phase;
  MatrixXd xds_phase;
  phase_system_->analyticalSolution(ts,xs_phase,xds_phase);
  
  // Compute gating term
  MatrixXd xs_gating;
  MatrixXd xds_gating;
  gating_system_->analyticalSolution(ts,xs_gating,xds_gating);

  // Compute the output of the function approximator
  fa_outputs.resize(ts.size(),dim_orig());
  fa_outputs.fill(0.0);
  //if (isTrained())
  computeFunctionApproximatorOutput(xs_phase, fa_outputs);

  MatrixXd xs_gating_rep = xs_gating.replicate(1,fa_outputs.cols());
  MatrixXd g_minus_y0_rep = (attractor_state()-initial_state()).transpose().replicate(n_time_steps,1);
  forcing_terms = fa_outputs.array()*xs_gating_rep.array(); // zzz *g_minus_y0_rep.array();
  
  MatrixXd xs_goal, xds_goal;
  // Get current delayed goal
  if (goal_system_==NULL)
  {
    // If there is no dynamical system for the delayed goal, the goal is
    // simply the attractor state               
    xs_goal  = attractor_state().transpose().replicate(n_time_steps,1);
    // with zero change
    xds_goal = MatrixXd::Zero(n_time_steps,dim_orig());
  } 
  else
  {
    // Integrate goal system and get current goal state
    goal_system_->analyticalSolution(ts,xs_goal,xds_goal);
  }

  xs.resize(n_time_steps,dim());
  xds.resize(n_time_steps,dim());

  int T = n_time_steps;
    
  xs.GOALM(T) = xs_goal;     xds.GOALM(T) = xds_goal;
  xs.PHASEM(T) = xs_phase;   xds.PHASEM(T) = xds_phase;
  xs.GATINGM(T) = xs_gating; xds.GATINGM(T) = xds_gating;

  
  // THE REST CANNOT BE DONE ANALYTICALLY
  
  // Reset the dynamical system, and get the first state
  double damping = spring_system_->damping_coefficient();
  SpringDamperSystem localspring_system_(tau(),initial_state(),attractor_state(),damping);
  
  // Set first attractor state
  localspring_system_.set_attractor_state(xs_goal.row(0));
  
  // Start integrating spring damper system
  int dim_spring = localspring_system_.dim();
  VectorXd x_spring(dim_spring), xd_spring(dim_spring); // zzz Why are these needed?
  int t0 = 0;
  localspring_system_.integrateStart(x_spring, xd_spring);
  xs.row(t0).SPRING  = x_spring;
  xds.row(t0).SPRING = xd_spring;

  // Add forcing term to the acceleration of the spring state  
  xds.SPRINGM_Z(1) = xds.SPRINGM_Z(1) + forcing_terms.row(t0)/tau();
  
  for (int tt=1; tt<n_time_steps; tt++)
  {
    double dt = ts[tt]-ts[tt-1];
    
    // Euler integration
    xs.row(tt).SPRING  = xs.row(tt-1).SPRING + dt*xds.row(tt-1).SPRING;
  
    // Set the attractor state of the spring system
    localspring_system_.set_attractor_state(xs.row(tt).GOAL);

    // Integrate spring damper system
    localspring_system_.differentialEquation(xs.row(tt).SPRING, xd_spring);
    xds.row(tt).SPRING = xd_spring;
    
    // Add forcing term to the acceleration of the spring state
    xds.row(tt).SPRING_Z = xds.row(tt).SPRING_Z + forcing_terms.row(tt)/tau();
    // Compute y component from z
    xds.row(tt).SPRING_Y = xs.row(tt).SPRING_Z/tau();
    
  } 
}

void Dmp::computeFunctionApproximatorInputsAndTargets(const Trajectory& trajectory, VectorXd& fa_inputs_phase, MatrixXd& f_target) const
{
  int n_time_steps = trajectory.length();
  double dim_data = trajectory.dim();
  
  if (dim_orig()!=dim_data)
  {
    cout << "WARNING: Cannot train " << dim_orig() << "-D DMP with " << dim_data << "-D data. Doing nothing." << endl;
    return;
  }
  
  // Integrate analytically to get goal, gating and phase states
  MatrixXd xs_ana;
  MatrixXd xds_ana;
  
  // Before, we would make clone of the dmp, and integrate it with the tau, and initial/attractor
  // state of the trajectory. However, Thibaut needed to call this from outside the Dmp as well,
  // with the tau/states of the this object. Therefore, we no longer clone. 
  // Dmp* dmp_clone = static_cast<Dmp*>(this->clone());
  // dmp_clone->set_tau(trajectory.duration());
  // dmp_clone->set_initial_state(trajectory.initial_y());
  // dmp_clone->set_attractor_state(trajectory.final_y());
  // dmp_clone->analyticalSolution(trajectory.ts(),xs_ana,xds_ana);
  analyticalSolution(trajectory.ts(),xs_ana,xds_ana);
  MatrixXd xs_goal   = xs_ana.GOALM(n_time_steps);
  MatrixXd xs_gating = xs_ana.GATINGM(n_time_steps);
  MatrixXd xs_phase  = xs_ana.PHASEM(n_time_steps);
  
  fa_inputs_phase = xs_phase;
  
  // Get parameters from the spring-dampers system to compute inverse
  double damping_coefficient = spring_system_->damping_coefficient();
  double spring_constant     = spring_system_->spring_constant();
  double mass                = spring_system_->mass();
  if (mass!=1.0)
  {
    cout << "WARNING: Usually, spring-damper system of the DMP should have mass==1, but it is " << mass << endl;
  }

  // Compute inverse
  f_target = tau()*tau()*trajectory.ydds() + (spring_constant*(trajectory.ys()-xs_goal) + damping_coefficient*tau()*trajectory.yds())/mass;
  
  //Factor out gating term
  for (unsigned int dd=0; dd<function_approximators_.size(); dd++)
    f_target.col(dd) = f_target.col(dd).array()/xs_gating.array();
 
}

void Dmp::train(const Trajectory& trajectory)
{
  train(trajectory,"");
}

void Dmp::train(const Trajectory& trajectory, string save_directory, bool overwrite)
{
  
  // Set tau, initial_state and attractor_state from the trajectory 
  set_tau(trajectory.duration());
  set_initial_state(trajectory.initial_y());
  set_attractor_state(trajectory.final_y());
  
  VectorXd fa_input_phase;
  MatrixXd f_target;
  computeFunctionApproximatorInputsAndTargets(trajectory, fa_input_phase, f_target);
  
  // Some checks before training function approximators
  assert(!function_approximators_.empty());
  
  for (unsigned int dd=0; dd<function_approximators_.size(); dd++)
  {
    // This is just boring stuff to figure out if and where to store the results of training
    string save_directory_dim;
    if (!save_directory.empty())
    {
      if (function_approximators_.size()==1)
        save_directory_dim = save_directory;
      else
        save_directory_dim = save_directory + "/dim" + boost::lexical_cast<string>(dd);
    }
    
    // Actual training is happening here.
    VectorXd fa_target = f_target.col(dd);
    if (function_approximators_[dd]->isTrained())
      function_approximators_[dd]->reTrain(fa_input_phase,fa_target,save_directory_dim,overwrite);
    else
      function_approximators_[dd]->train(fa_input_phase,fa_target,save_directory_dim,overwrite);
  }
}

void Dmp::getSelectableParameters(set<string>& selected_values_labels) const {
  assert(function_approximators_.size()>0);
  // zzz Assumes all FAs are the same. Should rather return entire set.
  function_approximators_[0]->getSelectableParameters(selected_values_labels);  
}

void Dmp::setSelectedParameters(const set<string>& selected_values_labels)
{
  // nnn add assert
  for (int dd=0; dd<dim_orig(); dd++)
    function_approximators_[dd]->setSelectedParameters(selected_values_labels);
}

void Dmp::getParameterVectorMask(const std::set<std::string> selected_values_labels, Eigen::VectorXi& selected_mask) const
{
  cout << __FILE__ << ":" << __LINE__ << ":Here" << endl;

  selected_mask.resize(getParameterVectorAllSize());
  selected_mask.fill(0);
  
  int offset = 0;
  VectorXi cur_mask;
  for (int dd=0; dd<dim_orig(); dd++)
  {
    function_approximators_[dd]->getParameterVectorMask(selected_values_labels,cur_mask);
    selected_mask.segment(offset,cur_mask.size()) = cur_mask;
    offset += cur_mask.size();
  }
  //nnn Check for multi-dim dmps

  assert(offset == getParameterVectorAllSize());   
}

int Dmp::getParameterVectorAllSize(void) const
{
  int total_size = 0;
  for (unsigned int dd=0; dd<function_approximators_.size(); dd++)
    total_size += function_approximators_[dd]->getParameterVectorAllSize();
  return total_size;
}


void Dmp::getParameterVectorAll(VectorXd& values) const
{
  values.resize(getParameterVectorAllSize());
  int offset = 0;
  VectorXd cur_values;
  for (int dd=0; dd<dim_orig(); dd++)
  {
    function_approximators_[dd]->getParameterVectorAll(cur_values);
    values.segment(offset,cur_values.size()) = cur_values;
    offset += cur_values.size();
  }
}

void Dmp::setParameterVectorAll(const VectorXd& values)
{
  assert(values.size()==getParameterVectorAllSize());
  int offset = 0;
  VectorXd cur_values;
  for (int dd=0; dd<dim_orig(); dd++)
  {
    int n_parameters_required = function_approximators_[dd]->getParameterVectorAllSize();
    cur_values = values.segment(offset,n_parameters_required);
    function_approximators_[dd]->setParameterVectorAll(cur_values);
    offset += n_parameters_required;
  }
}

void Dmp::getModelParametersVectors(vector<VectorXd>& model_parameters, bool normalized) const
{
  model_parameters.clear();
  VectorXd model_parameters_vector;
  for (int dd=0; dd<dim_orig(); dd++)
  {
    function_approximators_[dd]->getParameterVectorSelected(model_parameters_vector, normalized);
    model_parameters.push_back(model_parameters_vector);
  }
}

void Dmp::setModelParametersVectors(const vector<VectorXd>& model_parameters, bool normalized)
{
  for (int dd=0; dd<dim_orig(); dd++)
    function_approximators_[dd]->setParameterVectorSelected(model_parameters[dd], normalized);
}



void Dmp::set_tau(double tau) {
  DynamicalSystem::set_tau(tau);

  // Set value in all relevant subsystems also  
  spring_system_->set_tau(tau);
  if (goal_system_!=NULL)
    goal_system_->set_tau(tau);
  phase_system_ ->set_tau(tau);
  gating_system_->set_tau(tau);
}

void Dmp::set_initial_state(const VectorXd& y_init) {
  DynamicalSystem::set_initial_state(y_init);
  
  // Set value in all relevant subsystems also  
  spring_system_->set_initial_state(y_init);
  if (goal_system_!=NULL)
    goal_system_->set_initial_state(y_init);
}    

void Dmp::set_attractor_state(const VectorXd& y_attr) {
  DynamicalSystem::set_attractor_state(y_attr);
  
  // Set value in all relevant subsystems also  
  if (goal_system_!=NULL)
    goal_system_->set_attractor_state(y_attr);

  // Do NOT do the following. The attractor state of the spring system is determined by the goal 
  // system
  // spring_system_->set_attractor_state(y_attr);

}    


ostream& Dmp::serialize(ostream& output) const
{
  output << "{ \"Dmp\": {";
  output << "\"name\": \"" << name() << "\", ";
  output << "\"tau\" : "  << tau()  << ", ";
  output << "\"dim\" : "  << dim()  << ", ";
  output << "\"dim_orig\" : "  << dim_orig()  << ", ";
  output << "\"y_init\" : " << serializeJSON(initial_state()) << ", ";
  output << "\"y_attr\" : " << serializeJSON(attractor_state()) << ", ";
  output << "\"spring_system\": " << *spring_system_ << ", ";
  if (goal_system_ ==NULL)
    output << "\"goal_system\": "   << "{}" << ", ";
  else
    output << "\"goal_system\": "   << *goal_system_ << ", ";
  output << "\"phase_system\": "  << *phase_system_  << ", ";
  output << "\"gating_system\": " << *gating_system_ << ", ";
  output << "\"function_approximators\": [";
  for (int dd=0; dd<dim_orig(); dd++)
  {
    output << (*function_approximators_[dd]);
    if (dd<dim_orig()-1) output << ", ";
  }
  output << "]";
  output << " } }";
  return output;  // for multiple << operators.
}


Dmp* Dmp::deserialize(istream& input)
{
  cout << __FILE__ << ":" << __LINE__ << ":NOT IMPLEMENTED YET!" << endl;
  return NULL;
  
  // nnn Implement this
  
  //static const boost::regex must_match(".*\\{ *\"name\": *(.*?), *\"tau\": *(.*?), *\"dim\": *(.*?), *\"dim_orig\": *(.*?) *, *\"y_init\": *(.*?) *, *\"y_attr\": *(.*?) *, *\"goal_system\": *(.*?) *, *\"phase_system\": *(.*?) *, *\"gating_system\": *(.*?) *, *\"function_approximators\": *(.*?) *\\}"); 
  static const boost::regex must_match(".*\\{ *\"name\": *\"(.*?)\" *, *\"tau\" *: *(.*?), *\"dim\" *: *(.*?), *\"dim_orig\" *: *(.*?), *\"y_init\" *: *(.*?), *\"y_attr\" *: *(.*?) *, *\"spring_system\" *: *(.*?) *, *\"goal_system\" *: *(.*?) *, *\"phase_system\" *: *(.*?) *, *\"gating_system\" *: *(.*?) *, *\"function_approximators\": *(.*? *]) *\\} *\\}"); 
  boost::match_results<std::string::const_iterator> results;
  
  string input_string;
  
  boost::regex match_name(".*\\{ *\"name\": *\"");
  while (input.good() && !boost::regex_match(input_string, results, match_name))
    input_string += input.get();
  input_string.clear();
  
  string name;
  input >> name;
    
  cout << name << endl;
  
  exit(0);
    
  /*  
    if (false && boost::regex_match(input_string, results, must_match))
    {
      string name = results[1]; 
      double tau =  boost::lexical_cast<double>(results[2]); 
      int dim =  boost::lexical_cast<int>(results[3]); 
      int dim_orig =  boost::lexical_cast<int>(results[4]); 
      MatrixXd y_init, y_attr;
      deserializeMatrixJSON(results[5],y_init);
      deserializeMatrixJSON(results[6],y_attr);
      
      stringstream strstream1(results[7]);
      DynamicalSystem* spring_system = deserializeDynamicalSystem(strstream1);

      DynamicalSystem* goal_system;
      stringstream strstream2(results[8]);
      if (results[8].compare("{}")==0)
        goal_system = NULL;
      else
        goal_system = deserializeDynamicalSystem(strstream2);

      stringstream strstream3(results[9]);
      DynamicalSystem* phase_system = deserializeDynamicalSystem(strstream3);

      stringstream strstream4(results[10]);
      DynamicalSystem* gating_system = deserializeDynamicalSystem(strstream4);

      string str = results[11];
      cout << str << endl;
      
      exit(0);
      
      
      cout << endl;
      cout << input_string << endl;
      cout << name << endl;
      cout << tau << endl;
      cout << dim << endl;
      cout << dim_orig << endl;
      cout << y_init << endl;
      cout << y_attr << endl;
      cout << *spring_system << endl;
      cout << *goal_system << endl;
      cout << *phase_system << endl;
      cout << *gating_system << endl;
      cout << results[11] << endl;

      //vector<FunctionApproximator*> function_approximators(2);
      //Dmp bla(tau, y_init, y_attr, function_approximators, Dmp::KULVICIUS_2012_JOINING); 
      //cout << "  bla=" << bla << endl;

      exit(0);
      
      
      MatrixXd centers, widths, offsets, slopes;
      deserializeMatrixJSON(results[1],centers);
      deserializeMatrixJSON(results[2],widths);
      deserializeMatrixJSON(results[3],slopes);
      deserializeMatrixJSON(results[4],offsets);
      //return new Dmp(centers,widths,slopes,offsets);
    }  
  }
  */

  return NULL;
}
