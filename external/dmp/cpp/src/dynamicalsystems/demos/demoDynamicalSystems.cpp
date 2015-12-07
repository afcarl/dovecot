/**
 * \file demoDynamicalSystems.cpp
 * \author Freek Stulp
 * \brief  Demonstrates how to initialize, integrate, perturb all implemented exponential systems.
 *
 * \ingroup Demos
 * \ingroup DynamicalSystems
 */

#include "dynamicalsystems/ExponentialSystem.h"
#include "dynamicalsystems/SigmoidSystem.h"
#include "dynamicalsystems/TimeSystem.h"
#include "dynamicalsystems/SpringDamperSystem.h"

#include "utilities/EigenFileIO.hpp"

#include <iostream>
#include <iomanip>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

void runDynamicalSystemTest(const DynamicalSystem* dyn_system_input, string test_label, VectorXd& ts, MatrixXd& xs, MatrixXd& xds)
{
  // Make a clone that we can modify
  DynamicalSystem* dyn_system = dyn_system_input->clone();
  
  
  // Settings for the integration of the system
  double dt = 0.004; // Integration step duration
  double integration_duration = 1.5*dyn_system->tau(); // Integrate for longer than the time constant
  int n_time_steps = ceil(integration_duration/dt)+1; // Number of time steps for the integration
  // Generate a vector of times, i.e. 0.0, dt, 2*dt, 3*dt .... n_time_steps*dt=integration_duration
  ts = VectorXd::LinSpaced(n_time_steps,0.0,integration_duration);


  if (test_label.compare("tau")==0)
    dyn_system->set_tau(0.5*dyn_system->tau());
  
  if (test_label.compare("euler")==0)
    dyn_system->set_integration_method(DynamicalSystem::EULER);

  // Dimensionality of the current system
  int n_dims = dyn_system->dim();
      
  xs.resize(n_dims,n_time_steps);               
  xds.resize(n_dims,n_time_steps);

  if (test_label.compare("analytical")==0)
  {
    // ANALYTICAL SOLUTION 
    dyn_system->analyticalSolution(ts,xs,xds);
    return;
  }
      
  // NUMERICAL INTEGRATION 
  dyn_system->integrateStart(xs.col(0),xds.col(0));
  for (int ii=1; ii<n_time_steps; ii++)
  {
    if (test_label.compare("attractor")==0)
      if (ii==ceil(0.3*n_time_steps))
        dyn_system->set_attractor_state(-0.2+dyn_system->attractor_state().array());
      
    if (test_label.compare("perturb")==0)
      if (ii==ceil(0.3*n_time_steps))
        xs.col(ii-1) = xs.col(ii-1).array()-0.2;
  
    dyn_system->integrateStep(dt,xs.col(ii-1),xs.col(ii),xds.col(ii)); 
  }

  
}

int main(int n_args, char** args)
{

  // PARSE INPUT ARGUMENTS AND SEE WHETHER TO WRITE TO A DIRECTORY
  vector<string> available_test_labels;
  available_test_labels.push_back("rungekutta");
  available_test_labels.push_back("euler");
  available_test_labels.push_back("analytical");
  available_test_labels.push_back("tau");
  available_test_labels.push_back("attractor");
  available_test_labels.push_back("perturb");
  
  if (n_args<2)
  {
    cout << "Usage:    " << args[0] << " <directory> [test label 1]  [test label 2]" << endl;
    cout <<      "                 available test labels = ";
    for (unsigned int i_test=0; i_test<available_test_labels.size(); i_test++)
      cout << "'" << available_test_labels[i_test] << "', ";
    cout << endl;
    cout << "Example: " << args[0] << " /tmp/runDynamicalSystemsDemo rungekutta" << endl << endl;
    return -1;
  }
  
  // Which directory to write data to
  string directory = string(args[1]); // args[1] exists, already checked above
  bool overwrite=true; // If there are already results in the directory, overwrite them.

  // Which test to perform
  vector<string> test_labels;
  if (n_args>2) 
    test_labels.push_back(string(args[2]));
  if (n_args>3) 
    test_labels.push_back(string(args[3]));
  else
    test_labels = available_test_labels;
  
  cout << "  test_labels.size()=" << test_labels.size() << endl;
  
  // FILL AN ARRAY WITH DYNAMICAL SYSTEMS
  
  // Array with different dynamical system implementations
  int n_systems = 4;
  DynamicalSystem* dyn_systems[n_systems];
  
  // ExponentialSystem
  double tau = 0.6; // Time constant
  VectorXd initial_state(2);   initial_state   << 0.5, 1.0; 
  VectorXd attractor_state(2); attractor_state << 0.8, 0.1; 
  double alpha = 6.0; // Decay factor
  dyn_systems[0] = new ExponentialSystem(tau, initial_state, attractor_state, alpha);
  
  // TimeSystem
  dyn_systems[1] = new TimeSystem(tau);

  // SigmoidSystem
  double max_rate = -20;
  double inflection_point = tau*0.8;
  dyn_systems[2] = new SigmoidSystem(tau, initial_state, max_rate, inflection_point);
  
  // SpringDamperSystem
  alpha = 12.0;
  dyn_systems[3] = new SpringDamperSystem(tau, initial_state, attractor_state, alpha);

  
  // INTEGRATE ALL DYNAMICAL SYSTEMS IN THE ARRAY AND OUTPUT RESULTS


  // Variables that will be used in the loop
  string filename, first_filename, save_directory;
  ofstream output_file;
  VectorXd ts;
  MatrixXd xs, xds;
  
  // Loop through all systems, and do numerical integration and compute the analytical solution
  for (int i_system=0; i_system<n_systems; i_system++)
  {
    for (unsigned int i_test=0; i_test<test_labels.size(); i_test++)
    {
      // RUN THE CURRENT TEST FOR THE CURRENT SYSTEM
      runDynamicalSystemTest(dyn_systems[i_system], test_labels[i_test], ts, xs, xds);
      
      // WRITE RESULTS TO FILE
      
      // Put the results in one matrix to facilitate the writing of the data
      MatrixXd xs_xds_ts(ts.size(),1+2*dyn_systems[i_system]->dim());
      xs_xds_ts << xs.transpose(), xds.transpose(), ts;
    
      save_directory = directory+"/"+dyn_systems[i_system]->name();
      filename = "results_"+test_labels[i_test]+".txt";
      saveMatrix(save_directory,filename,xs_xds_ts,overwrite);
      //saveMatrix(save_directory,"dim_orig.txt",VectorXd::Constant(1,dyn_systems[i_test]->dim_orig()),overwrite);

      cout << "Use 'cd ../plotting/ ; python plotDynamicalSystem.py " << save_directory << "/" << filename << "' to plot the results." << endl;
      if (i_test==0)
        first_filename = filename;
      else
        cout << "Use 'cd ../plotting/ ; python plotDynamicalSystemComparison.py " << save_directory << "/" << first_filename << " " << save_directory << "/" << filename << "' to plot a comparison of the results." << endl;
      cout << endl;

    }
    cout << endl;

  }

  
  for (int i_system=0; i_system<n_systems; i_system++)
    delete dyn_systems[i_system]; 
  
  return 0;
}
