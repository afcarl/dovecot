/**
 * @file   MetaParametersGMR.h
 * @brief  MetaParametersGMR class source file.
 * @author Freek Stulp, Thibaut Munzer
 */

#include "functionapproximators/MetaParametersGMR.h"

#include <iostream>

#include <boost/lexical_cast.hpp>
#include "utilities/ParseJSON.hpp"

using namespace std;

MetaParametersGMR::MetaParametersGMR(int expected_input_dim, int number_of_gaussians) 
	:
    MetaParameters(expected_input_dim),
    number_of_gaussians_(number_of_gaussians)
{
}

MetaParametersGMR* MetaParametersGMR::clone(void) const {
  return new MetaParametersGMR(getExpectedInputDim(),number_of_gaussians_);
}

		
ostream& MetaParametersGMR::serialize(ostream& output) const {
  output << "{ \"MetaParametersGMR\": {";
  output << "\"expected_input_dim\": " << getExpectedInputDim() << ", ";
  output << "\"number_of_gaussians\": " << number_of_gaussians_;
  output << " } }";
  return output;
}


MetaParametersGMR* MetaParametersGMR::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);
  
  if (json_string.empty())
    return NULL;
  
  int expected_input_dim= boost::lexical_cast<int>(getJSONValue(json_string,"expected_input_dim"));
  int number_of_gaussians=boost::lexical_cast<int>(getJSONValue(json_string,"number_of_gaussians"));

  return new MetaParametersGMR(expected_input_dim, number_of_gaussians);
}


