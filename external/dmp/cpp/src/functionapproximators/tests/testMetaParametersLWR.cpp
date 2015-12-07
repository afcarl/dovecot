#include "functionapproximators/MetaParametersLWR.h"
#include "functionapproximators/ModelParametersLWR.h"
//#include "functionapproximators/FunctionApproximatorLWR.h"

#include "utilities/EigenFileIO.hpp"
#include "utilities/EigenJSON.hpp"
#include "../demos/targetFunction.hpp"

#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <eigen3/Eigen/Core>
#include <boost/filesystem.hpp>

using namespace std;
using namespace Eigen;

int main(int n_args, char** args)
{
  string directory;
  double overlap = 0.05;
  int n_dims = 1;
  
  if (n_args>1)
    directory = string(args[1]);
  if (n_args>2)
    n_dims = atoi(args[2]);
  if (n_args>3)
    overlap = atof(args[3]);
    
  
  // Generete the activations of the basis functions and save to file
  VectorXi n_samples_per_dim = VectorXi::Constant(1,200);
  if (n_dims==2) 
    n_samples_per_dim = VectorXi::Constant(2,20);
    
  MatrixXd inputs, targets; // Not really interested in targets, but useful to get inputs
  targetFunction(n_samples_per_dim,inputs,targets);
  
  VectorXd min = inputs.colwise().minCoeff();
  VectorXd max = inputs.colwise().maxCoeff();
  
    
  MatrixXd centers, widths;
  MetaParametersLWR* mp;
  if (n_dims==1)
  {
    // Try constructor for 1D input data.
    int n_bfs = 9;
    mp = new MetaParametersLWR(n_dims,n_bfs,overlap); 
  }
  else
  {
    // Try constructor for N-D input data.
    
    // First constructor for N-D input data: specify only number of basis functions per dimension
    VectorXi n_bfs_per_dim(n_dims);
    n_bfs_per_dim[0] = 3;
    n_bfs_per_dim[1] = 5;
    mp = new MetaParametersLWR(n_dims,n_bfs_per_dim,overlap);
    cout << *mp << endl;
    delete mp; // Free memory to try other constructor
    
    // Second constructor for N-D input data: specify centers of the basis functions per dimension
    vector<VectorXd> centers_per_dim(n_dims);
    for (int i_dim=0; i_dim<n_dims; i_dim++)
      centers_per_dim[i_dim] = VectorXd::LinSpaced(n_bfs_per_dim[i_dim],min[i_dim],max[i_dim]);
     mp = new MetaParametersLWR(n_dims,centers_per_dim,overlap); 
  }
  
  
  cout << *mp << endl;
  mp->getCentersAndWidths(min,max,centers,widths);
  cout << "centers = " << serializeJSON(centers) << endl;
  cout << "widths  = " <<  serializeJSON(widths) << endl;
  delete mp;
}

