#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <time.h>
#include <boost/filesystem.hpp>

#include "functionapproximators/FunctionApproximator.h"

#include "getFunctionApproximatorsVector.h"
#include "../demos/targetFunction.hpp"

using namespace std;
using namespace Eigen;

int main(int n_args, char** args)
{
  string directory;
  if (n_args>1)
    directory = string(args[1]);
  
  vector<string> fa_names;
  if (n_args>2)
  {
    for (int aa=2; aa<n_args; aa++)
      fa_names.push_back(string(args[aa]));
  }
  else
  {
    fa_names.push_back("LWR");
    fa_names.push_back("LWPR");
    fa_names.push_back("GMR");
    fa_names.push_back("IRFRLS");
  }
        
  
  for (int n_input_dims=1; n_input_dims<=2; n_input_dims++)
  {
    cout << "___________________________________________________________________" << endl;
    cout << "Using " << n_input_dims << "-D data.   " << endl;
    
    VectorXi n_samples_per_dim = VectorXi::Constant(1,10);
    if (n_input_dims==2) 
      n_samples_per_dim = VectorXi::Constant(2,25);
    
    MatrixXd inputs, targets, outputs;
    targetFunction(n_samples_per_dim,inputs,targets);
    
    
    for (unsigned int i_name=0; i_name<fa_names.size(); i_name++)
    {
      FunctionApproximator* cur_fa = getFunctionApproximatorByName(fa_names[i_name],n_input_dims);
      if (cur_fa==NULL)
        continue;
  
      string save_directory;
      if (!directory.empty())
        save_directory = directory+"/"+cur_fa->getName()+"_"+(n_input_dims==1?"1D":"2D");
      
      cout << "Training " << cur_fa->getName() << endl;
      cur_fa->train(inputs,targets,save_directory);

      
      // Do predictions and compute mean absolute error
      cur_fa->predict(inputs,outputs);

      MatrixXd abs_error = (targets.array()-outputs.array()).abs();
      VectorXd mean_abs_error_per_output_dim = abs_error.colwise().mean();
     
      cout << fixed << setprecision(5);
      cout << "         Mean absolute error ";
      if (mean_abs_error_per_output_dim.size()>1) cout << " (per dimension)";
      cout << ": " << mean_abs_error_per_output_dim.transpose();      
      cout << "   \t(range of target data is " << targets.colwise().maxCoeff().array()-targets.colwise().minCoeff().array() << ")";
      
      cout << endl;
      
      delete cur_fa;

      if (!directory.empty())
      {
        cout << "        ______________________________________________________________" << endl;
        cout << "        | Plot saved data with:" << " 'python testFunctionApproximatorTraining.py " << save_directory << "'." << endl;
        cout << "        |______________________________________________________________" << endl;
      }
    }
  
  }
  
  return 0;
}


