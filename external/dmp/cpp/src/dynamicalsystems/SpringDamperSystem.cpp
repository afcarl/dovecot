/**
 * @file   SpringDamperSystem.cpp
 * @brief  SpringDamperSystem class source file.
 * @author Freek Stulp
 */
 

#include "dynamicalsystems/SpringDamperSystem.h"

#include <cmath>
#include <iostream>
#include <eigen3/Eigen/Core>

#include "utilities/EigenJSON.hpp"

using namespace std;
using namespace Eigen;

SpringDamperSystem::SpringDamperSystem(double tau, VectorXd y_init, VectorXd y_attr, double damping_coefficient, double spring_constant, double mass, string name)
  : DynamicalSystem(2, tau, y_init, y_attr, name),
  damping_coefficient_(damping_coefficient),spring_constant_(spring_constant),mass_(mass)
{
  if (spring_constant_==CRITICALLY_DAMPED)
    spring_constant_ = damping_coefficient_*damping_coefficient_/4; // Critically damped
}

SpringDamperSystem::~SpringDamperSystem(void)
{
}

DynamicalSystem* SpringDamperSystem::clone(void) const
{
  return new SpringDamperSystem(tau(),initial_state(),attractor_state(),
                        damping_coefficient_,spring_constant_,mass_,name());
}

void SpringDamperSystem::differentialEquation(const VectorXd& x, Ref<VectorXd> xd) const
{
  // Spring-damper system was originally 2nd order, i.e. with [x xd xdd]
  // After rewriting it as a 1st order system it becomes [y z yd zd], with yd = z; 
      
  // Get 'y' and 'z' parts of the state in 'x'
  int dim2 = dim()/2;
  VectorXd y = x.segment(0,dim2);
  VectorXd z = x.segment(dim2,dim2);
  VectorXd y_attr = attractor_state().segment(0,dim2);
  
  // Compute yd and zd
  // See  http://en.wikipedia.org/wiki/Damped_spring-mass_system#Example:mass_.E2.80.93spring.E2.80.93damper
  // and equation 2.1 of http://www-clmc.usc.edu/publications/I/ijspeert-NC2013.pdf

  VectorXd yd = z/tau();
  
  VectorXd zd = (-spring_constant_*(y-y_attr) - damping_coefficient_*z)/(mass_*tau());
  
  xd.segment(0,dim()/2) = yd;
  xd.segment(dim()/2,dim()/2) = zd;
      
}

void SpringDamperSystem::analyticalSolution(const VectorXd& ts, MatrixXd& xs, MatrixXd& xds) const
{
  int T = ts.size();

  // Usually, we expect xs and xds to be of size T X dim(), so we resize to that. However, if the
  // input matrices were of size dim() X T, we return the matrices of that size by doing a 
  // transposeInPlace at the end. That way, the user can also request dim() X T sized matrices.
  bool caller_expects_transposed = (xs.rows()==dim() && xs.cols()==T);

  // Prepare output arguments to be of right size (Eigen does nothing if already the right size)
  xs.resize(T,dim());
  xds.resize(T,dim());

  VectorXd y_init = initial_state();
  VectorXd y_attr = attractor_state();
  
  // Closed form solution to 2nd order canonical system
  // This system behaves like a critically damped spring-damper system
  // http://en.wikipedia.org/wiki/Damped_spring-mass_system
  double omega_0 = sqrt(spring_constant_/mass_)/tau(); // natural frequency
  double zeta    = damping_coefficient_/(2*sqrt(mass_*spring_constant_)); // damping ratio
  if (zeta!=1.0)
    cout << "WARNING: Spring-damper system is not critically damped, zeta=" << zeta << endl;
      
  // Example
  //  _______________
  //    dim = 4
  //  _______
  //  dim2= 2
  // [y_1 y_2 z_1 z_2 yd_1 yd_2 zd_1 zd_2]
  
  int dim2 = dim()/2;

  // The loop is slower, but more legible than fudging around with Eigen::replicate().
  for (int i_dim=0; i_dim<dim2; i_dim++)
  {
    double y0 = y_init[i_dim] - y_attr[i_dim];
    double yd0;
    if (y_init.size()>=dim())
    {
      // Initial velocities also given
      yd0 = y_init[dim2 + i_dim];          
    }
    else
    {
      // Initial velocities not given: set to zero
      yd0 = 0.0;
    }
          
    double A = y0;
    double B = yd0 + omega_0*y0;
    
    // Closed form solutions
    // See http://en.wikipedia.org/wiki/Damped_spring-mass_system
    VectorXd exp_term  = -omega_0*ts;
    exp_term = exp_term.array().exp();
  
    int Y  = 0*dim2 + i_dim;
    int Z  = 1*dim2 + i_dim;
   
    VectorXd ABts = A + B*ts.array();
    
    // Closed form solutions
    // See http://en.wikipedia.org/wiki/Damped_spring-mass_system
    // If you find this illegible, I recommend to look at the Matlab code instead...
    xs.col(Y)  =  y_attr(i_dim) +      ((   ABts.array()))*exp_term.array();
                                                    
    // Derivative of the above (use product rule: (f*g)' = f'*g + f*g'
    xds.col(Y) =                    ((B - omega_0*   ABts.array()))*exp_term.array();
                                                    
    // Derivative of the above (again use product    rule: (f*g)' = f'*g + f*g'
    VectorXd ydds   =    (-omega_0*(2*B - omega_0*   ABts.array()))*exp_term.array();
      
    // This is how to compute the 'z' terms from the 'y' terms
    xs.col(Z)  = xds.col(Y)*tau();
    xds.col(Z) = ydds*tau();
  }
        
  if (caller_expects_transposed)
  {
    xs.transposeInPlace();
    xds.transposeInPlace();
  }
}


ostream& SpringDamperSystem::serialize(ostream& output) const
{
  output << "{ \"SpringDamperSystem\": {";
  output << "\"name\": \"" << name() << "\", ";
  output << "\"tau\" : "  << tau()  << ", ";
  output << "\"y_init\" : " << serializeJSON(initial_state()) << ", ";
  output << "\"y_attr\" : " << serializeJSON(attractor_state()) << ", ";
  output << "\"damping_coefficient\" : "  << damping_coefficient_  << ", ";
  output << "\"spring_constant\" : "  << spring_constant_ << ", ";
  output << "\"mass\" : "  << mass_;
  output << " } }";
  return output;  // for multiple << operators.
}


DynamicalSystem* SpringDamperSystem::deserialize(istream& input)
{
  string name;
  double tau;
  MatrixXd y_init;
  MatrixXd y_attr;
  double damping_coefficient;
  double spring_constant;
  double mass;
  
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
  input >> y_attr;               
                                 
  input.ignore(100,':');         
  input >> damping_coefficient;                

  input.ignore(100,':');         
  input >> spring_constant;                

  input.ignore(100,':');         
  input >> mass;                

  input.ignore(100,'}');         
  
  //cout << name << " " << tau << " [" << y_init.transpose() << "]  [" << y_attr.transpose() << "]" << " " << damping_coefficient << " " << spring_constant << " " << mass << endl;

  return new SpringDamperSystem(tau,y_init,y_attr,damping_coefficient,spring_constant,mass,name);
}
