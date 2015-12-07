#include "getDynamicalSystemsVector.h"

#include "dynamicalsystems/DynamicalSystem.h"

#include <iostream>
#include <fstream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;
  
int main(int n_args, char** args)
{
  vector<DynamicalSystem*> dyn_systems;
  getDynamicalSystemsVector(dyn_systems);
  
  for (unsigned int dd=0; dd<dyn_systems.size(); dd++)
  {
    DynamicalSystem* cur_dyn_system = dyn_systems[dd]; 
    DynamicalSystem* cloned = dyn_systems[dd]->clone(); 
    
    cout << "Original:" << endl << "    " << *cur_dyn_system << endl;
    
    // Delete current dynamical system to see if it doesn't delete memory in the clone
    delete cur_dyn_system;
    
    cloned->set_initial_state(cloned->initial_state());
    cloned->set_tau(cloned->tau());
    cout << "   Clone:" << endl << "    " << *cloned << endl;
    delete cloned;
    
  }
}

