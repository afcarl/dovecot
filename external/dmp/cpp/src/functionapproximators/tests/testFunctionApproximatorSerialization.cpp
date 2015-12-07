#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <time.h>
#include <boost/filesystem.hpp>

#include "functionapproximators/ModelParameters.h"
#include "functionapproximators/MetaParameters.h"
#include "functionapproximators/FunctionApproximator.h"
#include "functionapproximators/deserializeFunctionApproximator.h"

#include "getFunctionApproximatorsVector.h"
#include "../demos/targetFunction.hpp"

using namespace std;
using namespace Eigen;

int main(int n_args, char** args)
{
  vector<string> fa_names;
  if (n_args>1)
  {
    for (int aa=1; aa<n_args; aa++)
      fa_names.push_back(string(args[aa]));
  }
  else
  {
    fa_names.push_back("LWR");
    fa_names.push_back("LWPR");
    // zzz fa_names.push_back("GMR");
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
      cout << "______________________________________________" << endl;
      stringstream stream;
      MetaParameters* cur_mepa = getMetaParametersByName(fa_names[i_name],n_input_dims);
      if (cur_mepa==NULL)
        continue;
      stream << *cur_mepa;
      cout << "cur_mepa: " << stream.str() << endl << endl;
      
      MetaParameters* new_mepa;
      stream >> new_mepa;
      if (new_mepa!=NULL)
        cout << "new_mepa: " << *new_mepa << endl << endl;
      
      cout << endl;
      
      stringstream stream2;
      FunctionApproximator* cur_fa = getFunctionApproximatorByName(fa_names[i_name],n_input_dims);
      if (cur_fa==NULL)
        continue;
      stream2 << *cur_fa;
      cout << "cur_fa: " << stream2.str() << endl << endl;
      FunctionApproximator* new_fa;
      stream2 >> new_fa; 
      if (new_fa!=NULL)
        cout << "new_fa: " << *new_fa << endl << endl;
            
      cout << endl;
      
      
      
      stringstream stream3;
      cout << "Training function approximator to compute model parameters." << endl;
      cur_fa->train(inputs,targets);
      
      const ModelParameters* cur_mopa = cur_fa->getModelParameters();
      stream3 << *cur_mopa;
      cout << "cur_mopa: " << stream3.str() << endl << endl;
      
      ModelParameters* new_mopa;
      stream3 >> new_mopa; 
      if (new_mopa!=NULL)
        cout << "new_mopa: " << *new_mopa << endl << endl;
    
      cout << endl;
      
      stringstream stream4;
      if (cur_fa==NULL)
        continue;
      cout << "cur_fa: " << *cur_fa << endl << endl;
      stream4 << *cur_fa;
      stream4 >> new_fa;
      if (new_fa!=NULL)
        cout << "new_fa: " << *new_fa << endl << endl;
  
      cout << endl;
      
    }
  
  }
  
  return 0;
}


