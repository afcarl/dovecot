/**
 * @file   MetaParametersLWPR.h
 * @brief  MetaParametersLWPR class source file.
 * @author Freek Stulp
 */
 
#include "functionapproximators/MetaParametersLWPR.h"

#include "utilities/EigenJSON.hpp"
#include "utilities/ParseJSON.hpp"

#include <iostream>

#include <boost/lexical_cast.hpp>

using namespace Eigen;
using namespace std;

MetaParametersLWPR::MetaParametersLWPR(
    int expected_input_dim, 
    VectorXd init_D, double w_gen, double w_prune,
    bool update_D, double init_alpha, double penalty, bool diag_only,
    bool use_meta, double meta_rate, string kernel_name
  )
:
  MetaParameters(expected_input_dim),
  init_D_(init_D), w_gen_(w_gen), w_prune_(w_prune),
  update_D_(update_D), init_alpha_(init_alpha), penalty_(penalty), diag_only_(diag_only),
  use_meta_(use_meta), meta_rate_(meta_rate), kernel_name_(kernel_name)
{
  assert(init_D_.size()==expected_input_dim);
  assert(w_gen_>0.0 && w_gen_<1.0);
  assert(w_prune_>0.0 && w_prune_<1.0);
  assert(w_gen_<w_prune_);
}

MetaParametersLWPR* MetaParametersLWPR::clone(void) const
{
  return new MetaParametersLWPR(
    getExpectedInputDim(), 
    init_D_, w_gen_, w_prune_,
    update_D_, init_alpha_, penalty_, diag_only_,
    use_meta_, meta_rate_, kernel_name_
  );  
}

ostream& MetaParametersLWPR::serialize(ostream& output) const {
  output << "{ \"MetaParametersLWPR\" : {";
  output << "\"expected_input_dim\": " << getExpectedInputDim() << ", ";
  output << "\"init_D\": " << serializeJSON(init_D_) << ", ";
  output << "\"w_gen\": " << w_gen_ << ", ";
  output << "\"w_prune\": " << w_prune_ << ", ";
  output << "\"update_D\": " << update_D_ << ", ";
  output << "\"init_alpha\": " << init_alpha_ << ", ";
  output << "\"penalty\": " << penalty_ << ", ";
  output << "\"diag_only\": " << diag_only_ << ", ";
  output << "\"use_meta\": " << use_meta_ << ", ";
  output << "\"meta_rate\": " << meta_rate_ << ", ";
  output << "\"kernel_name\": \"" << kernel_name_ << "\"";  
  output << " } }";
  return output;
}

MetaParametersLWPR* MetaParametersLWPR::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);

  if (json_string.empty())
    return NULL;
  
  int expect_dim;
  double w_gen, w_prune, init_alpha, penalty, meta_rate;
  bool update_D, diag_only, use_meta;
  string kernel_name;
  MatrixXd init_D;

  expect_dim  = boost::lexical_cast<int>   (getJSONValue(json_string,"expected_input_dim"));
  deserializeMatrixJSON                    (getJSONValue(json_string,"init_D"),init_D);
  w_gen       = boost::lexical_cast<double>(getJSONValue(json_string,"w_gen"));
  w_prune     = boost::lexical_cast<double>(getJSONValue(json_string,"w_prune"));
    
  update_D    = boost::lexical_cast<bool>  (getJSONValue(json_string,"update_D"));
  init_alpha  = boost::lexical_cast<double>(getJSONValue(json_string,"init_alpha"));
  penalty     = boost::lexical_cast<double>(getJSONValue(json_string,"penalty"));
  diag_only   = boost::lexical_cast<bool>  (getJSONValue(json_string,"diag_only"));
              
  use_meta    = boost::lexical_cast<bool>  (getJSONValue(json_string,"use_meta"));
  meta_rate   = boost::lexical_cast<double>(getJSONValue(json_string,"meta_rate"));
  kernel_name = getJSONValue(json_string,"kernel_name");
  
  return new MetaParametersLWPR(
    expect_dim,
    init_D, w_gen, w_prune,
    update_D, init_alpha, penalty, diag_only,
    use_meta, meta_rate, kernel_name);
  
}

