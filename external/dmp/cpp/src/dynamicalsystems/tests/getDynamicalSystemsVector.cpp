#include "getDynamicalSystemsVector.h"

#include "dynamicalsystems/DynamicalSystem.h"
#include "dynamicalsystems/ExponentialSystem.h"
#include "dynamicalsystems/SigmoidSystem.h"
#include "dynamicalsystems/TimeSystem.h"
#include "dynamicalsystems/SpringDamperSystem.h"

#include <vector>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

void getDynamicalSystemsVector(vector<DynamicalSystem*>& dyn_systems)
{
  // ExponentialSystem
  double tau = 0.6; // Time constant
  VectorXd initial_state(2);   initial_state   << 0.5, 1.0; 
  VectorXd attractor_state(2); attractor_state << 0.8, 0.1; 
  double alpha = 6.0; // Decay factor
  dyn_systems.push_back(new ExponentialSystem(tau, initial_state, attractor_state, alpha));
  
  // TimeSystem
  dyn_systems.push_back(new TimeSystem(tau));

  // SigmoidSystem
  double max_rate = -20;
  double inflection_point = tau*0.8;
  dyn_systems.push_back(new SigmoidSystem(tau, initial_state, max_rate, inflection_point));
  
  // SpringDamperSystem
  alpha = 12.0;
  dyn_systems.push_back(new SpringDamperSystem(tau, initial_state, attractor_state, alpha));
}
