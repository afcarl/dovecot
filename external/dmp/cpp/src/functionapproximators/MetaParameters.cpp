/**
 * @file   MetaParameters.h
 * @brief  MetaParameters class source file.
 * @author Freek Stulp
 */
 
#include <iostream>
#include <assert.h>

#include "functionapproximators/MetaParameters.h"

using namespace std;

MetaParameters::MetaParameters(int expected_input_dim)
: expected_input_dim_(expected_input_dim)
{
  assert(expected_input_dim_>0);
}

ostream& operator<<(ostream& output, const MetaParameters& meta_parameters) {
  return meta_parameters.serialize(output);
}

