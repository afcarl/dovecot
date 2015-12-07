/**
 * @file   DynamicalSystem.cpp
 * @brief  DynamicalSystem class source file.
 * @author Freek Stulp
 */
 
#include "dynamicalsystems/DynamicalSystem.h"

#include <cmath>
#include <iostream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

DynamicalSystem::DynamicalSystem(int order, double tau, VectorXd initial_state, VectorXd attractor_state, string name)
  : 
  // For 1st order systems, the dimensionality of the state vector 'x' is 'dim'
  // For 2nd order systems, the system is expanded to x = [y z], where 'y' and
  // 'z' are both of dimensionality 'dim'. Therefore dim(x) is 2*dim
  dim_(initial_state.size()*order),
  // The dimensionality of the system before a potential rewrite
  dim_orig_(initial_state.size()),
  tau_(tau),initial_state_(initial_state),attractor_state_(attractor_state),
  name_(name),integration_method_(RUNGE_KUTTA)
{
  assert(initial_state.size()==attractor_state.size());
}

DynamicalSystem::~DynamicalSystem(void)
{
}

void DynamicalSystem::integrateStart(const VectorXd& x_init, Ref<VectorXd> x, Ref<VectorXd> xd)
{
  set_initial_state(x_init);
  integrateStart(x,xd);
}

void DynamicalSystem::integrateStart(Ref<VectorXd> x, Ref<VectorXd> xd) const {
  
  // Return value for state variables
  // Pad the end with zeros: Why? In the spring-damper system, the state consists of x = [y z]. 
  // The initial state only applies to y. Therefore, we set x = [y 0]; 
  x.fill(0);
  x.segment(0,initial_state_.size()) = initial_state_;
  
  // Return value (rates of change)
  differentialEquation(x,xd);
}

void DynamicalSystem::integrateStep(double dt, const Ref<const VectorXd> x, Ref<VectorXd> x_updated, Ref<VectorXd> xd_updated) const
{
  if (integration_method_ == RUNGE_KUTTA)
    integrateStepRungeKutta(dt, x, x_updated, xd_updated);
  else
    integrateStepEuler(dt, x, x_updated, xd_updated);
}


void DynamicalSystem::integrateStepEuler(double dt, const Ref<const VectorXd> x, Ref<VectorXd> x_updated, Ref<VectorXd> xd_updated) const
{
  // simple Euler integration
  differentialEquation(x,xd_updated);
  x_updated  = x + dt*xd_updated;
}

void DynamicalSystem::integrateStepRungeKutta(double dt, const Ref<const VectorXd> x, Ref<VectorXd> x_updated, Ref<VectorXd> xd_updated) const
{
  // 4th order Runge-Kutta for a 1st order system
  // http://en.wikipedia.org/wiki/Runge-Kutta_method#The_Runge.E2.80.93Kutta_method
  
  int l = x.size();
  VectorXd k1(l), k2(l), k3(l), k4(l);
  differentialEquation(x,k1);
  VectorXd input_k2 = x + dt*0.5*k1;
  differentialEquation(input_k2,k2);
  VectorXd input_k3 = x + dt*0.5*k2;
  differentialEquation(input_k3,k3);
  VectorXd input_k4 = x + dt*k3;
  differentialEquation(input_k4,k4);
      
  x_updated = x + dt*(k1 + 2.0*(k2+k3) + k4)/6.0;
  differentialEquation(x_updated,xd_updated); 
}

