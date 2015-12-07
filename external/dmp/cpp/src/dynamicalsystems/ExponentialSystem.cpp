/**
 * @file   ExponentialSystem.cpp
 * @brief  ExponentialSystem class source file.
 * @author Freek Stulp
 */

#include "dynamicalsystems/ExponentialSystem.h"

#include <cmath>
#include <vector>
#include <iostream>
#include <eigen3/Eigen/Core>

#include "utilities/EigenJSON.hpp"

using namespace std;
using namespace Eigen;  

ExponentialSystem::ExponentialSystem(double tau, VectorXd y_init, VectorXd y_attr, double alpha, string name)
  : DynamicalSystem(1, tau, y_init, y_attr, name),
  alpha_(alpha)
{
}

ExponentialSystem::~ExponentialSystem(void)
{
}

DynamicalSystem* ExponentialSystem::clone(void) const
{
  return new ExponentialSystem(tau(),initial_state(),attractor_state(),alpha_,name());
}


void ExponentialSystem::differentialEquation(const VectorXd& x, Ref<VectorXd> xd) const
{
  xd = alpha_*(attractor_state()-x)/tau();
}

void ExponentialSystem::analyticalSolution(const VectorXd& ts, MatrixXd& xs, MatrixXd& xds) const
{
  int T = ts.size();

  // Usually, we expect xs and xds to be of size T X dim(), so we resize to that. However, if the
  // input matrices were of size dim() X T, we return the matrices of that size by doing a 
  // transposeInPlace at the end. That way, the user can also request dim() X T sized matrices.
  bool caller_expects_transposed = (xs.rows()==dim() && xs.cols()==T);

  // Prepare output arguments to be of right size (Eigen does nothing if already the right size)
  xs.resize(T,dim());
  xds.resize(T,dim());
  
  VectorXd val_range = initial_state() - attractor_state();
  
  VectorXd exp_term  = -alpha_*ts/tau();
  exp_term = exp_term.array().exp().transpose();
  VectorXd pos_scale =                   exp_term;
  VectorXd vel_scale = -(alpha_/tau()) * exp_term;
  
  xs = val_range.transpose().replicate(T,1).array() * pos_scale.replicate(1,dim()).array();
  xs += attractor_state().transpose().replicate(T,1);
  xds = val_range.transpose().replicate(T,1).array() * vel_scale.replicate(1,dim()).array();
  
  if (caller_expects_transposed)
  {
    xs.transposeInPlace();
    xds.transposeInPlace();
  }
}


ostream& ExponentialSystem::serialize(ostream& output) const
{
  output << "{ \"ExponentialSystem\": {";
  output << "\"name\": \"" << name() << "\", ";
  output << "\"tau\": "  << tau() << ", ";
  output << "\"y_init\": " << serializeJSON(initial_state()) << ", ";
  output << "\"y_attr\": " << serializeJSON(attractor_state()) << ", ";
  output << "\"alpha\": "  << alpha_;
  output << " } }";
  return output;  // for multiple << operators.
}

DynamicalSystem* ExponentialSystem::deserialize(istream& input)
{
  string name;
  double tau;
  MatrixXd y_init;
  MatrixXd y_attr;
  double alpha;
  
  // {"name": "Expo", "tau": 0.6, "y_init": [[0.5],[1]], "y_attr": [[0.8],[0.1]], "alpha": 6 }
  char buffer[256];
  input.ignore(100,':'); 
  // "Expo", "tau": 0.6, "y_init": [[0.5],[1]], "y_attr": [[0.8],[0.1]], "alpha": 6 }
  input.ignore(100,'"'); 
  //  Expo", "tau": 0.6, "y_init": [[0.5],[1]], "y_attr": [[0.8],[0.1]], "alpha": 6 }
  input.get(buffer, 256, '"'); 
  //  buffer = Expo
  name = string(buffer);
  
  input.ignore(100,':');
  //                0.6, "y_init": [[0.5],[1]], "y_attr": [[0.8],[0.1]], "alpha": 6 }
  input >> tau;
  //                   , "y_init": [[0.5],[1]], "y_attr": [[0.8],[0.1]], "alpha": 6 }

  input.ignore(100,':');
  //                               [[0.5],[1]], "y_attr": [[0.8],[0.1]], "alpha": 6 }
  input >> y_init;               
  //                                          , "y_attr": [[0.8],[0.1]], "alpha": 6 }
                                 
  input.ignore(100,':');         
  //                                                      [[0.8],[0.1]], "alpha": 6 }
  input >> y_attr;               
  //                                                                   , "alpha": 6 }
                                 
  input.ignore(100,':');         
  //                                                                              6 }
  input >> alpha;                
  //                                                                                }
  input.ignore(100,'}');         
  //                                                                                           
  
  //cout << name << " " << tau << " [" << y_init.transpose() << "]  [" << y_attr.transpose() << "]" << " " << alpha << endl;
  
  return new ExponentialSystem(tau,y_init,y_attr,alpha,name);
}

