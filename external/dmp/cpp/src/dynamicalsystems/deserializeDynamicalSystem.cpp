#include "dynamicalsystems/deserializeDynamicalSystem.h"

#include <iostream>

#include "dynamicalsystems/ExponentialSystem.h"
#include "dynamicalsystems/TimeSystem.h"
#include "dynamicalsystems/SigmoidSystem.h"
#include "dynamicalsystems/SpringDamperSystem.h"


using namespace std;

DynamicalSystem* deserializeDynamicalSystem(istream &input)
{
  // Example { "ExponentialSystem": {"name": blablablabl.... } }  

  input.ignore(256,'"');
  char class_name[256];
  input.get(class_name, 256, '"');
  input.ignore(256,':');

  DynamicalSystem* dyn_sys = NULL;
  if (strcmp("ExponentialSystem",class_name)==0)
    dyn_sys = ExponentialSystem::deserialize(input);
  
  else if (strcmp("SigmoidSystem",class_name)==0)
    dyn_sys = SigmoidSystem::deserialize(input);
  
  else if (strcmp("TimeSystem",class_name)==0)
    dyn_sys = TimeSystem::deserialize(input);
  
  else if (strcmp("SpringDamperSystem",class_name)==0)
    dyn_sys = SpringDamperSystem::deserialize(input);
  
  else
  {
    cerr << __FILE__ << ":" << __LINE__ << ":ERROR: ";
    cerr << "Unknown dynamical system type '" << class_name << "'." << endl;
  }

  // Remove last bracket which we haven't read yet.  
  input.ignore(256,'}');

  return dyn_sys;
}

std::istream& operator>>(std::istream& input, DynamicalSystem*& dyn_sys)
{
  dyn_sys =  deserializeDynamicalSystem(input);
  return input;
}

