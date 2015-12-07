#include "getFunctionApproximatorsVector.h"

#include "functionapproximators/MetaParametersLWR.h"
#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/MetaParametersGMR.h"
#include "functionapproximators/FunctionApproximatorGMR.h"
#include "functionapproximators/MetaParametersIRFRLS.h"
#include "functionapproximators/FunctionApproximatorIRFRLS.h"
#ifdef USE_LWPR
#include "functionapproximators/MetaParametersLWPR.h"
#include "functionapproximators/FunctionApproximatorLWPR.h"
#endif // USE_LWPR

#include <vector>
#include <iostream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

void getFunctionApproximatorsVector(int input_dim, std::vector<FunctionApproximator*>& function_approximators)
{
  vector<string> names;
  names.push_back("LWR");
  names.push_back("LWPR");
  names.push_back("GMR");
  names.push_back("IRFRLS");

  for (unsigned int i_name=0; i_name<names.size(); i_name++)
  {
    FunctionApproximator* fa = getFunctionApproximatorByName(names[i_name],input_dim);
    if (fa!=NULL)
      function_approximators.push_back(fa);
  }
}

MetaParameters* getMetaParametersByName(string name, int input_dim)
{

  if (name.compare("LWR")==0)
  {
    // Locally Weighted Regression
    double overlap = 0.07;
    int n_rfs = 9;
    if (input_dim==2) n_rfs = 5;
    VectorXi num_rfs_per_dim = VectorXi::Constant(input_dim,n_rfs);
    return new MetaParametersLWR(input_dim,num_rfs_per_dim,overlap);
  } 

  if (name.compare("LWPR")==0)
  {
    // Locally Weighted Projection Regression
#ifdef USE_LWPR
    double   w_gen=0.2;
    double   w_prune=0.8;
    bool     update_D=true;
    double   init_alpha=0.1;
    double   penalty=0.1;
    VectorXd init_D=VectorXd::Constant(input_dim,20);
    return new MetaParametersLWPR(input_dim,init_D,w_gen,w_prune,update_D,init_alpha,penalty);
#else
    cerr << __FILE__ << ":" << __LINE__ << ":";
    cerr << "Sorry, LWPR is not available. Is it installed? Returning NULL." << endl;
    return NULL;
#endif // USE_LWPR
  }

  if (name.compare("GMR")==0)
  {
    // Gaussian Mixture Regression  
    int number_of_gaussians = 5;
    return new MetaParametersGMR(input_dim,number_of_gaussians);
  }
  
  if (name.compare("IRFRLS")==0)
  {
    // IRFRLS
    int number_of_basis_functions=40;
    double lambda=0.2;
    double gamma=10;
    return new MetaParametersIRFRLS(input_dim,number_of_basis_functions,lambda,gamma);
  }
  
  cerr << __FILE__ << ":" << __LINE__ << ":";
  cerr << "No meta parameters with name '" << name << "' is known. Returning NULL." << endl;
  return NULL;
}


FunctionApproximator* getFunctionApproximatorByName(string name, int input_dim)
{
  
  MetaParameters* meta_parameters = getMetaParametersByName(name, input_dim);
  
  if (name.compare("LWR")==0)
    return new FunctionApproximatorLWR(dynamic_cast<MetaParametersLWR*>(meta_parameters));

  if (name.compare("LWPR")==0)
  {
    // Locally Weighted Projection Regression
#ifdef USE_LWPR
    return new FunctionApproximatorLWPR(dynamic_cast<MetaParametersLWPR*>(meta_parameters));
#else
    cerr << __FILE__ << ":" << __LINE__ << ":";
    cerr << "Sorry, LWPR is not available. Is it installed? Returning NULL." << endl;
    return NULL;
#endif // USE_LWPR
  }

  if (name.compare("GMR")==0)
    return new FunctionApproximatorGMR(dynamic_cast<MetaParametersGMR*>(meta_parameters));
  
  if (name.compare("IRFRLS")==0)
    return new FunctionApproximatorIRFRLS(dynamic_cast<MetaParametersIRFRLS*>(meta_parameters));
  
  cerr << __FILE__ << ":" << __LINE__ << ":";
  cerr << "No function approximator with name '" << name << "' is known. Returning NULL." << endl;
  return NULL;
}
