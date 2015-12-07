/**
 * @file   SigmoidSystem.cpp
 * @brief  SigmoidSystem class source file.
 * @author Freek Stulp
 */

#include "dynamicalsystems/SigmoidSystem.h"

#include <cmath>
#include <vector>
#include <iostream>  
#include <eigen3/Eigen/Core>

#include "utilities/EigenJSON.hpp"

using namespace std;
using namespace Eigen;

SigmoidSystem::SigmoidSystem(double tau, const VectorXd& x_init, double max_rate, double inflection_point_time, string name)
: DynamicalSystem(1, tau, x_init, VectorXd::Zero(x_init.size()), name),
  max_rate_(max_rate),
  inflection_point_time_(inflection_point_time)
{
  Ks_ = SigmoidSystem::computeKs(initial_state(), max_rate_, inflection_point_time_);
}

SigmoidSystem::~SigmoidSystem(void)
{
}

DynamicalSystem* SigmoidSystem::clone(void) const
{
  return new SigmoidSystem(tau(),initial_state(),max_rate_,inflection_point_time_,name());
}

void SigmoidSystem::set_tau(double new_tau) {

  // Get previous tau from superclass with tau() and set it with set_tau()  
  double prev_tau = tau();
  DynamicalSystem::set_tau(new_tau);
  
  inflection_point_time_ = new_tau*inflection_point_time_/prev_tau; //zzz document this
  Ks_ = SigmoidSystem::computeKs(initial_state(), max_rate_, inflection_point_time_);
}

void SigmoidSystem::set_initial_state(const VectorXd& y_init) {
  assert(y_init.size()==dim_orig());
  DynamicalSystem::set_initial_state(y_init);
  Ks_ = SigmoidSystem::computeKs(initial_state(), max_rate_, inflection_point_time_);
}    

VectorXd SigmoidSystem::computeKs(const VectorXd& N_0s, double r, double inflection_point_time_time)
{
  // Known
  //   N(t) = K / ( 1 + (K/N_0 - 1)*exp(-r*t))
  //   N(t_inf) = K / 2
  // Plug into each other and solve for K
  //   K / ( 1 + (K/N_0 - 1)*exp(-r*t_infl)) = K/2
  //              (K/N_0 - 1)*exp(-r*t_infl) = 1
  //                             (K/N_0 - 1) = 1/exp(-r*t_infl)
  //                                       K = N_0*(1+(1/exp(-r*t_infl)))
  VectorXd Ks = N_0s;
  for (int dd=0; dd<Ks.size(); dd++)
    Ks[dd] = N_0s[dd]*(1+(1/exp(-r*inflection_point_time_time)));
  return Ks;
}

void SigmoidSystem::differentialEquation(const VectorXd& x, Ref<VectorXd> xd) const
{
  xd = max_rate_*x.array()*(1-(x.array()/Ks_.array()));
}

void SigmoidSystem::analyticalSolution(const VectorXd& ts, MatrixXd& xs, MatrixXd& xds) const
{
  int T = ts.size();

  // Usually, we expect xs and xds to be of size T X dim(), so we resize to that. However, if the
  // input matrices were of size dim() X T, we return the matrices of that size by doing a 
  // transposeInPlace at the end. That way, the user can also request dim() X T sized matrices.
  bool caller_expects_transposed = (xs.rows()==dim() && xs.cols()==T);

  // Prepare output arguments to be of right size (Eigen does nothing if already the right size)
  xs.resize(T,dim());
  xds.resize(T,dim());

  // Auxillary variables to improve legibility
  double r = max_rate_;
  VectorXd exp_rt = (-r*ts).array().exp();
  
  VectorXd y_init = initial_state();
      
  for (int dd=0; dd<dim(); dd++)
  {
    // Auxillary variables to improve legibility
    double K = Ks_[dd];
    double b = (K/y_init[dd])-1;
        
    xs.block(0,dd,T,1)  = K/(1+b*exp_rt.array());
    xds.block(0,dd,T,1) = K*r*b*((1 + b*exp_rt.array()).square().inverse().array()) * exp_rt.array();
  }
  
  if (caller_expects_transposed)
  {
    xs.transposeInPlace();
    xds.transposeInPlace();
  }
}


ostream& SigmoidSystem::serialize(ostream& output) const
{
  output << "{ \"SigmoidSystem\": {";
  output << "\"name\": \"" << name() << "\", ";
  output << "\"tau\": "  << tau()  << ", ";
  output << "\"y_init\": " << serializeJSON(initial_state()) << ", ";
  output << "\"max_rate\": "  << max_rate_  << ", ";
  output << "\"inflection_point_time\": "  << inflection_point_time_;
  output << " } }";
  return output;  // for multiple << operators.
}

DynamicalSystem* SigmoidSystem::deserialize(istream& input)
{
  string name;
  double tau;
  MatrixXd y_init;
  double max_rate;
  double inflection_point_time;
  
  // {"name": "Sig", "tau" : 0.6, "y_init" : [[0.5],[1]], "max_rate" : -20, "inflection_point_time" : 0.48 }
  
  char buffer[256];
  input.ignore(100,':'); 
  input.ignore(100,'"'); 
  input.get(buffer, 256, '"'); 
  name = string(buffer);
  
  input.ignore(100,':');
  input >> tau;
  
  input.ignore(100,':');
  input >> y_init;               
           
  input.ignore(100,':');
  input >> max_rate;                
  
  input.ignore(100,':');
  input >> inflection_point_time;                
  
  input.ignore(100,'}');         
  
  //cout << name << " " << tau << " [" << y_init.transpose() << "] " << max_rate << " " << inflection_point_time << endl;
  
  return new SigmoidSystem(tau,y_init,max_rate,inflection_point_time,name);

}



