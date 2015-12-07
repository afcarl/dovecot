/**
 * @file   MetaParametersIRFRLS.h
 * @brief  MetaParametersIRFRLS class source file.
 * @author Freek Stulp, Thibaut Munzer
 */

#include "functionapproximators/MetaParametersIRFRLS.h"

#include <iostream>

#include <boost/lexical_cast.hpp>
#include "utilities/ParseJSON.hpp"

using namespace std;

MetaParametersIRFRLS::MetaParametersIRFRLS(int expected_input_dim, int number_of_basis_functions, double lambda, double gamma) 
	:
    MetaParameters(expected_input_dim),
    number_of_basis_functions_(number_of_basis_functions),
    lambda_(lambda),
    gamma_(gamma)
{
}
		
MetaParametersIRFRLS* MetaParametersIRFRLS::clone(void) const {
  return new MetaParametersIRFRLS(getExpectedInputDim(),number_of_basis_functions_,lambda_,gamma_);
}

ostream& MetaParametersIRFRLS::serialize(ostream& output) const {
  output << "{ \"MetaParametersIRFRLS\": {";
  output << "\"expected_input_dim\": " << getExpectedInputDim() << ", ";
  output << "\"number_of_basis_functions\":" << number_of_basis_functions_ << ", ";
  output << "\"lambda\":" << lambda_ << ", ";
  output << "\"gamma\": " << gamma_ << "";
  output << " } }";
  return output;
}

MetaParametersIRFRLS* MetaParametersIRFRLS::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);

  if (json_string.empty())
    return NULL;
  
  int expect_dim, n_basis_functions;
  double lambda, gamma;
  
  expect_dim        = boost::lexical_cast<int>(getJSONValue(json_string,"expected_input_dim"));
  n_basis_functions = boost::lexical_cast<int>(getJSONValue(json_string,"number_of_gaussians"));
  lambda            = boost::lexical_cast<int>(getJSONValue(json_string,"lambda"));
  gamma             = boost::lexical_cast<int>(getJSONValue(json_string,"gamma"));
  
  return new MetaParametersIRFRLS(expect_dim, n_basis_functions, lambda, gamma);
}


