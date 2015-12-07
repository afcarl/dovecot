#include "getDynamicalSystemsVector.h"

#include "dynamicalsystems/DynamicalSystem.h"
#include "dynamicalsystems/deserializeDynamicalSystem.h"

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
    
    stringstream strstr;
    strstr << *cur_dyn_system << endl;
    
    DynamicalSystem* deserialized = deserializeDynamicalSystem(strstr);
    deserialized->set_tau(1.2);

    cout << "_____________________________________________________________________________" << endl;
    cout << "Original:" << endl << "    " << *cur_dyn_system << endl;
    cout << "Deserialized (with tau set to 1.2):" << endl << "    " << *deserialized << endl;
    
    delete cur_dyn_system;
    delete deserialized;
  }
}

