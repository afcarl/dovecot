#include "getFunctionApproximatorsVector.h"

#include "functionapproximators/FunctionApproximator.h"
#include "../demos/targetFunction.hpp"

#include <iostream>
#include <fstream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;


int main(int n_args, char** args)
{
  int n_input_dims = 1;
  vector<FunctionApproximator*> function_approximators;
  getFunctionApproximatorsVector(n_input_dims,function_approximators);

  VectorXi n_samples_per_dim = VectorXi::Constant(n_input_dims,50);
  MatrixXd inputs, targets;
  targetFunction(n_samples_per_dim, inputs, targets);
  
  for (unsigned int dd=0; dd<function_approximators.size(); dd++)
  {
    FunctionApproximator* cur_fa = function_approximators[dd]; 
    FunctionApproximator* cloned = cur_fa->clone(); 
    
    cout << endl <<  endl << "__________________________________________________________________________" << endl;
    
    cout << endl << "CLONED" << endl;
    cout << "Original   :" << endl << "    " << *cur_fa << endl;
    cout << "Clone      :" << endl << "    " << *cloned << endl;

    cout << endl << "TRAINING CLONE" << endl;
    cloned->train(inputs,targets);
    cout << "Original   :" << endl << "    " << *cur_fa << endl;
    cout << "Clone      :" << endl << "    " << *cloned << endl;

    cout << endl << "CLONE OF TRAINED CLONE" << endl;
    FunctionApproximator* cloned_cloned = cloned->clone(); 
    cout << "Original   :" << endl << "    " << *cur_fa << endl;
    cout << "Clone      :" << endl << "    " << *cloned << endl;
    cout << "Clone clone:" << endl << "    " << *cloned_cloned << endl;

    cout << endl << "DELETING CLONE" << endl;
    delete cloned;
    cout << "Original   :" << endl << "    " << *cur_fa << endl;
    cout << "Clone clone:" << endl << "    " << *cloned_cloned << endl;

    cout << endl << "DELETING ORIGINAL" << endl;
    delete cur_fa;
    cout << "Clone clone:" << endl << "    " << *cloned_cloned << endl;
    
    delete cloned_cloned;
    
  }
}

