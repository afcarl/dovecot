/**
 * \file demoExponentialSystem.cpp
 * \author Freek Stulp
 * \brief  Demonstrates how to initialize and integrate an exponential dynamical system.
 *
 * \ingroup Demos
 * \ingroup DynamicalSystems
 */

#include "dynamicalsystems/ExponentialSystem.h"

#include <iostream>
#include <iomanip>
#include <eigen3/Eigen/Core>

#include "utilities/EigenFileIO.hpp"

using namespace std;
using namespace Eigen;

int main(int n_args, char** args)
{
  // Settings for the exponential system
  double tau = 0.6;  // Time constant
  VectorXd initial_state(2);   initial_state   << 0.5, 1.0; 
  VectorXd attractor_state(2); attractor_state << 0.8, 0.1; 
  double alpha = 6.0; // Decay rate

  // Construct the system
  DynamicalSystem* system = new ExponentialSystem(tau, initial_state, attractor_state, alpha);
  

  // Settings for the integration of the system
  double dt = 0.004; // Integration step duration
  double integration_duration = 1.5*tau; // Integrate for longer than the time constant
  int n_time_steps = ceil(integration_duration/dt)+1; // Number of time steps for the integration
  // Generate a vector of times, i.e. 0.0, dt, 2*dt, 3*dt .... n_time_steps*dt=integration_duration
  VectorXd ts = VectorXd::LinSpaced(n_time_steps,0.0,integration_duration);

  
  // NUMERICAL INTEGRATION 
  
  int n_dims = system->dim(); // Dimensionality of the system
  MatrixXd xs_num(n_dims,n_time_steps);
  MatrixXd xds_num(n_dims,n_time_steps);

  // Use DynamicalSystemSystem::integrateStart to get the initial x and xd
  system->integrateStart(xs_num.col(0),xds_num.col(0));
  
  // Use DynamicalSystemSystem::integrateStep to integrate numerically step-by-step
  for (int ii=1; ii<n_time_steps; ii++)
    system->integrateStep(dt,xs_num.col(ii-1),xs_num.col(ii),xds_num.col(ii)); 
    //                               previous x       updated x      updated xd
    

  // ANALYTICAL SOLUTION 

  MatrixXd xs_ana(n_dims,n_time_steps);
  MatrixXd xds_ana(n_dims,n_time_steps);
  system->analyticalSolution(ts,xs_ana,xds_ana);

  // Write results to cout    
  for (int ii=0; ii<n_time_steps; ii+=(n_time_steps/20))
  {
    cout << fixed << setw(10) << setprecision(3);
    cout << xs_num.col(ii).transpose() << " " <<  xds_num.col(ii).transpose()<< " " ;
    cout << xs_ana.col(ii).transpose() << " " <<  xds_ana.col(ii).transpose() << " " ;
    cout << ts(ii) << endl;
  }
  
  cout << "        x_1         x_2        xd_1        xd_2         x_1         x_2        xd_1        xd_2           t" << endl;
  cout << "               NUMERICAL INTEGRATION            ||             ANALYTICAL SOLUTION                 ||  TIME " << endl;
  //cout << *system << endl;
    
  
  // First argument may be optional directory to write data to
  string directory;
  if (n_args>1) {
    directory = string(args[1]);
    bool overwrite = true;
    
    // Put the results in one matrix to facilitate the writing of the data
    MatrixXd xs_xds_ts(ts.size(),1+2*system->dim());
    
    xs_xds_ts << xs_ana.transpose(), xds_ana.transpose(), ts;
    saveMatrix(directory,"analytical.txt",xs_xds_ts,overwrite);
    
    xs_xds_ts << xs_num.transpose(), xds_num.transpose(), ts;
    saveMatrix(directory,"numerical.txt",xs_xds_ts,overwrite);
  }
      
  delete system; 
  
  return 0;
}
