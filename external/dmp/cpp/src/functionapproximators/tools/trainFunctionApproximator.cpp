#include "functionapproximators/FunctionApproximator.h"
#include "functionapproximators/deserializeFunctionApproximator.h"

#include "utilities/EigenFileIO.hpp"

#include <iostream>
#include <fstream>
#include <string>
#include <time.h>
#include <stdexcept>

using namespace std;
using namespace Eigen;

string fa_file_json;
string inputs_file_txt;
string targets_file_txt;
string fa_file_json_out;

bool parsearguments(int n_args, char* args[]);

int main(int n_args, char** args)
{
  if (!parsearguments(n_args,args))
    return -1;
  
  // Open file 
  ifstream file_stream(fa_file_json);
  if (!file_stream.good())
    throw runtime_error(string("Couldn't open '"+fa_file_json+"'."));
  
  // Read function approximator from file stream
  FunctionApproximator* fa;  
  file_stream >> fa;

  // Read inputs and targets from file  
  MatrixXd inputs, targets;
  if (!loadMatrix(inputs_file_txt,inputs))
    return -1;

  if (!loadMatrix(targets_file_txt,targets))
    return -1;

  // Train the function approximator (and time how long it takes)
  clock_t t;
  t = clock();
  fa->train(inputs,targets);
  t = clock() - t;

  // Print to cout or file
  if (fa_file_json_out.empty())
  {
    // Don't print anything else here in case people want to pipe this to somewhere
    cout << *fa << endl;
  }
  else
  {
    ofstream file_stream(fa_file_json_out);
    if (!file_stream.good())
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "Couldn't open " << fa_file_json_out << endl;
      return -1;
    }
    file_stream << *fa;

    cout << endl <<  "Saved trained function approximator to '" << fa_file_json_out << "'" << endl;
    
    MatrixXd outputs;
    fa->predict(inputs,outputs);
    
    MatrixXd abs_error = (targets.array()-outputs.array()).abs();
    VectorXd mean_abs_error_per_output_dim = abs_error.colwise().mean();
   
    //cout << fixed << setprecision(5);
    cout << "    Mean absolute error on training data ";
    if (mean_abs_error_per_output_dim.size()>1) cout << " (per dimension)";
    cout << ": " << mean_abs_error_per_output_dim.transpose() << endl;      
    cout << "    Range of target data is " << targets.colwise().maxCoeff().array()-targets.colwise().minCoeff().array() << "";
    cout << endl;
    cout << "    Training took " << t << " clicks (" << ((float)t)/CLOCKS_PER_SEC <<  " seconds)." << endl << endl;
    

  }
    
  
  return 0;
}


bool parsearguments(int n_args, char* args[])
{

  // Usage
  if (n_args<4)
  {
    cout << "Usage: " << args[0] << " <functionapproximator.json> <inputs.txt> <targets.txt> [functionapproximator_trained.json]" << endl; 
    cout << "      Reads a function approximator from a JSON file, trains it with the data in the TXT files." << endl;
    cout << "      Then outputs the trained function approximator as JSON (to cout, or optionally functionapproximator_trained.json file)" << endl;
    return false;
  }

  // Not using boost::program_options, to reduce dependencies 
  
  // Get arguments
  fa_file_json = string(args[1]);
  inputs_file_txt = string(args[2]);
  targets_file_txt = string(args[3]);
  if (n_args>4)
    fa_file_json_out = string(args[4]);
  

  return true;
  
}


