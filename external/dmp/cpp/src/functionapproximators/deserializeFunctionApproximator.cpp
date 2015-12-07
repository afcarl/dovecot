#include "functionapproximators/deserializeFunctionApproximator.h"

#include "functionapproximators/MetaParametersLWR.h"
#include "functionapproximators/MetaParametersLWPR.h"
#include "functionapproximators/MetaParametersGMR.h"
#include "functionapproximators/MetaParametersIRFRLS.h"

#include "functionapproximators/ModelParametersLWR.h"
#include "functionapproximators/ModelParametersLWPR.h"
#include "functionapproximators/ModelParametersGMR.h"
#include "functionapproximators/ModelParametersIRFRLS.h"

#include "functionapproximators/FunctionApproximatorLWR.h"
#include "functionapproximators/FunctionApproximatorLWPR.h"
#include "functionapproximators/FunctionApproximatorGMR.h"
#include "functionapproximators/FunctionApproximatorIRFRLS.h"

#include "utilities/ParseJSON.hpp"

#include <iostream>
#include <stdexcept>



using namespace std;

std::istream& operator>>(std::istream& input, MetaParameters*& meta_parameters)
{
  // Example { "MetaParametersLWR": {"name": blablablabl.... } }  

  input.ignore(256,'"');
  char class_name[256];
  input.get(class_name, 256, '"');
  input.ignore(256,':');

  meta_parameters = NULL;
  if (strcmp("MetaParametersLWR",class_name)==0)
    meta_parameters = MetaParametersLWR::deserialize(input);
  
#ifdef USE_LWPR
  else if (strcmp("MetaParametersLWPR",class_name)==0)
    meta_parameters = MetaParametersLWPR::deserialize(input);
#endif // USE_LWPR
  
  else if (strcmp("MetaParametersGMR",class_name)==0)
    meta_parameters = MetaParametersGMR::deserialize(input);
  
  else if (strcmp("MetaParametersIRFRLS",class_name)==0)
    meta_parameters = MetaParametersIRFRLS::deserialize(input);
  
  else
  {
    throw std::runtime_error(string("Unknown MetaParameters class '")+class_name+"'.");
  }
  
  input.ignore(256,'}');

  return input;
}


std::istream& operator>>(std::istream& input, ModelParameters*& model_parameters)
{
  // Example { "ModelParametersLWR": {"name": blablablabl.... } }  

  input.ignore(256,'{');
  char c = input.peek(); 
  if (c=='}')
  {
    // This means the input was "{}", so return NULL 
    model_parameters = NULL;
    return input;
  }
  
  input.ignore(256,'"');
  char class_name[256];
  input.get(class_name, 256, '"');
  input.ignore(256,':');
  

  if (strcmp("ModelParametersLWR",class_name)==0)
    model_parameters = ModelParametersLWR::deserialize(input);
  
#ifdef USE_LWPR
  else if (strcmp("ModelParametersLWPR",class_name)==0)
    model_parameters = ModelParametersLWPR::deserialize(input);
#endif // USE_LWPR
  
  /* nnn
  else if (strcmp("ModelParametersGMR",class_name)==0)
    model_parameters = ModelParametersGMR::deserialize(input);
    */
    
  else if (strcmp("ModelParametersIRFRLS",class_name)==0)
    model_parameters = ModelParametersIRFRLS::deserialize(input);

  else
  {
    throw std::runtime_error(string("Unknown ModelParameters class '")+class_name+"'.");
  }
  
  input.ignore(256,'}');

  return input;
}


std::istream& operator>>(std::istream& input, FunctionApproximator*& function_approximator)
{

  // Example { "FunctionApproximatorLWR": {"meta_parameters": { "MetaParametersLWR": {...}, "model_parameters" :{} } }
  
  // zzz Make this prettier and more robust
  
  input.ignore(256,'"');
  char class_name[256];
  input.get(class_name, 256, '"');
  input.ignore(256,':');
  input.ignore(256,':');
  input.ignore(256,'{');
  // We are now at "MetaParametersLWR...
  MetaParameters* meta_parameters;
  input >> meta_parameters;
  
  input.ignore(256,':');
  ModelParameters* model_parameters;
  input >> model_parameters;

  FunctionApproximator* fa = NULL;
  if (strcmp("FunctionApproximatorLWR",class_name)==0)
  {
    if (model_parameters!=NULL)
      fa = new FunctionApproximatorLWR(dynamic_cast<MetaParametersLWR*>(meta_parameters),dynamic_cast<ModelParametersLWR*>(model_parameters));
    else
      fa = new FunctionApproximatorLWR(dynamic_cast<MetaParametersLWR*>(meta_parameters));
  }
  
#ifdef USE_LWPR
  else if (strcmp("FunctionApproximatorLWPR",class_name)==0)
    fa = new FunctionApproximatorLWPR(dynamic_cast<MetaParametersLWPR*>(meta_parameters));
#endif // USE_LWPR
  
  else if (strcmp("FunctionApproximatorGMR",class_name)==0)
    fa = new FunctionApproximatorGMR(dynamic_cast<MetaParametersGMR*>(meta_parameters));
    
  else if (strcmp("FunctionApproximatorIRFRLS",class_name)==0)
    fa = new FunctionApproximatorIRFRLS(dynamic_cast<MetaParametersIRFRLS*>(meta_parameters));
    
  else
  {
    throw std::runtime_error(string("Unknown FunctionApproximator class '")+class_name+"'.");
  }
  
  input.ignore(256,'}');

  function_approximator = fa;
  
  return input;
}

