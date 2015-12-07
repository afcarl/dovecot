#include "functionapproximators/FunctionApproximator.h"
#include "functionapproximators/deserializeFunctionApproximator.h"

#include "utilities/EigenFileIO.hpp"

#include <iostream>
#include <fstream>
#include <string>
#include <time.h>


using namespace std;
using namespace Eigen;

string fa_file_json;
string inputs_file_txt;
string outputs_file_txt;

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
  
  if (!fa->isTrained())
  {
    cerr << __FILE__ << ":" << __LINE__ << ":";
    cerr << "Cannot make predictions because function approximator in " << fa_file_json << " has  not been trained." << endl;
    return -1;
  }
    

  // Read inputs and targets from file  
  MatrixXd inputs, outputs;
  if (!loadMatrix(inputs_file_txt,inputs))
    return -1;

  // Train the function approximator (and time how long it takes)
  clock_t t;
  t = clock();
  fa->predict(inputs,outputs);
  t = clock() - t;

  // Print to cout or file
  if (outputs_file_txt.empty())
  {
    // Don't print anything else here in case people want to pipe this to somewhere
    cout << outputs << endl;
  }
  else
  {
    saveMatrix(outputs_file_txt,outputs);

    cout << endl <<  "Saved predictions to '" << outputs_file_txt << "'" << endl;
    cout << "    Prediction took " << t << " clicks (" << ((float)t)/CLOCKS_PER_SEC <<  " seconds)." << endl << endl;
    

  }
    
  
  return 0;
}

bool parsearguments(int n_args, char* args[])
{
  // Usage
  if (n_args<3)
  {
    cout << "Usage: " << args[0] << " <functionapproximator.json> <inputs.txt> [outputs.txt] [functionapproximator_trained.json]" << endl; 
    cout << "      Reads a trained function approximator from a JSON file, and makes predictions for the data in inputs.txt files." << endl;
    cout << "      Then outputs the predictions (to cout, or optionally to the outputs.txt file)" << endl;
    return false;
  }

  // Get arguments
  fa_file_json = string(args[1]);
  inputs_file_txt = string(args[2]);
  if (n_args>3)
    outputs_file_txt = string(args[3]);
  
  return true;
}


