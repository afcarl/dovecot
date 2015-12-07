#include "dmp/Dmp.h"
#include "dmp/Trajectory.h"

#include "dynamicalsystems/DynamicalSystem.h"
#include "dynamicalsystems/ExponentialSystem.h"
#include "dynamicalsystems/SigmoidSystem.h"
#include "dynamicalsystems/TimeSystem.h"
#include "dynamicalsystems/SpringDamperSystem.h"

#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/MetaParametersLWR.h"
#include "functionapproximators/ModelParametersLWR.h"

#include <iostream>
#include <fstream>


using namespace std;
using namespace Eigen;


int main(int n_args, char** args)
{

  // Generate a trajectory 
  double tau = 0.5;
  int n_time_steps = 51;
  VectorXd ts = VectorXd::LinSpaced(n_time_steps,0,tau); // Time steps
  int n_dims;
  Trajectory trajectory;
  
  bool use_viapoint_traj= false;
  if (use_viapoint_traj)
  {
    n_dims = 1;
    VectorXd y_first = VectorXd::Zero(n_dims);
    VectorXd y_last  = VectorXd::Ones(n_dims);
    double viapoint_time = 0.25;
    double viapoint_location = 0.5;
  
    VectorXd y_yd_ydd_viapoint = VectorXd::Zero(3*n_dims);
    y_yd_ydd_viapoint.segment(0*n_dims,n_dims).fill(viapoint_location); // y         
    trajectory = Trajectory::generatePolynomialTrajectoryThroughViapoint(ts,y_first,y_yd_ydd_viapoint,viapoint_time,y_last); 
  }
  else
  {
    n_dims = 2;
    VectorXd y_first = VectorXd::LinSpaced(n_dims,0.0,0.7); // Initial state
    VectorXd y_last  = VectorXd::LinSpaced(n_dims,0.4,0.5); // Final state
    trajectory = Trajectory::generateMinJerkTrajectory(ts, y_first, y_last);
  }
  
  
  
  // Initialize some meta parameters for training LWR function approximator
  int n_basis_functions = 3;
  int input_dim = 1;
  double overlap = 0.01;
  MetaParametersLWR* meta_parameters = new MetaParametersLWR(input_dim,n_basis_functions,overlap);      
  FunctionApproximatorLWR* fa_lwr = new FunctionApproximatorLWR(meta_parameters);  
  
  // Clone the function approximator for each dimension of the DMP
  vector<FunctionApproximator*> function_approximators(n_dims);    
  for (int dd=0; dd<n_dims; dd++)
    function_approximators[dd] = fa_lwr->clone();
  
  // Initialize the DMP
  Dmp* dmp = new Dmp(n_dims, function_approximators, Dmp::KULVICIUS_2012_JOINING);

  cout << "cout    : " << *dmp << endl;
  stringstream strstream;
  strstream << *dmp << endl;
  Dmp* dmp_new = Dmp::deserialize(strstream);
  cout << "dmp_new : " << *dmp_new << endl;

  
  // And train it. Passing the save_directory will make sure the results are saved to file.
  //dmp->train(trajectory);

  delete meta_parameters;
  delete fa_lwr;
  delete dmp;

  return 0;
}
