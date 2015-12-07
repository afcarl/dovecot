/**
 * @file   TimeSystem.cpp
 * @brief  TimeSystem class source file.
 * @author Freek Stulp
 */

#include "dynamicalsystems/TimeSystem.h"

#include <cmath>
#include <vector>
#include <iostream>
#include <eigen3/Eigen/Core>

#include "utilities/EigenJSON.hpp"

using namespace std;
using namespace Eigen;

TimeSystem::TimeSystem(double tau, string name)
: DynamicalSystem(1, tau, VectorXd::Zero(1), VectorXd::Ones(1), name)
{
}

TimeSystem::~TimeSystem(void)
{
}

DynamicalSystem* TimeSystem::clone(void) const
{
  return new TimeSystem(tau(),name());
}

void TimeSystem::differentialEquation(const VectorXd& x, Ref<VectorXd> xd) const
{
  // if state<1: xd = 1/obj.tau
  // else        xd = 0
  xd = VectorXd::Zero(1);
  if (x[0]<1)
    xd[0] = 1.0/tau();
}

#include<stdio.h>
void TimeSystem::analyticalSolution(const VectorXd& ts, MatrixXd& xs, MatrixXd& xds) const
{
  int T = ts.size();

  // Usually, we expect xs and xds to be of size T X dim(), so we resize to that. However, if the
  // input matrices were of size dim() X T, we return the matrices of that size by doing a 
  // transposeInPlace at the end. That way, the user can also request dim() X T sized matrices.
  bool caller_expects_transposed = (xs.rows()==dim() && xs.cols()==T);

  // Prepare output arguments to be of right size (Eigen does nothing if already the right size)
  xs.resize(T,dim());
  xds.resize(T,dim());
  
  // Find first index at which the time is larger than tau. Then velocities should be set to zero.
  int velocity_stop_index = -1;
  int i=0;
  while (velocity_stop_index<0 && i<ts.size())
    if (ts[i++]>tau())
      velocity_stop_index = i-1;
    
  if (velocity_stop_index<0)
    velocity_stop_index = ts.size();
    
  xs.topRows(velocity_stop_index) = ts.segment(0,velocity_stop_index).array()/tau();
  xs.bottomRows(xs.size()-velocity_stop_index).fill(1.0);

  xds.topRows(velocity_stop_index).fill(1.0/tau());
  xds.bottomRows(xds.size()-velocity_stop_index).fill(0.0);
  
  if (caller_expects_transposed)
  {
    xs.transposeInPlace();
    xds.transposeInPlace();
  }
}


ostream& TimeSystem::serialize(ostream& output) const
{
  output << "{ \"TimeSystem\": {";
  output << "\"name\": \"" << name() << "\", ";
  output << "\"tau\" : "  << tau() ;
  output << " } }";
  return output;  // for multiple << operators.
}

DynamicalSystem* TimeSystem::deserialize(istream& input)
{
  string name;
  double tau;
  
  // {"name": "TimeSystemName", "tau" : 0.6 }
  char buffer[256];                        
  input.ignore(100,':');                   
  //          "TimeSystemName", "tau" : 0.6 }
  input.ignore(100,'"');                   
  //           TimeSystemName", "tau" : 0.6 }
  input.get(buffer, 256, '"');             
  // buffer = TimeSystemName               
  name = string(buffer);                   
                                           
  input.ignore(100,':');                   
  //                                    0.6 }
  input >> tau;                            
  //                                        }
  
  input.ignore(100,'}');         
  //                                             
  
  //cout << name << " " << tau << endl;
  
  return new TimeSystem(tau,name);
}


