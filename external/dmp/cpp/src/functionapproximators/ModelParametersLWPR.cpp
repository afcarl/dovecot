/**
 * @file   ModelParametersLWPR.h
 * @brief  ModelParametersLWPR class source file.
 * @author Freek Stulp, Thibaut Munzer
 */
 
#include "functionapproximators/ModelParametersLWPR.h"

#include "utilities/ParseJSON.hpp"
#include "utilities/EigenJSON.hpp"

#include "lwpr.hh"
#include <boost/regex.hpp>


#include <iostream>
#include <fstream>

using namespace Eigen;
using namespace std;

ModelParametersLWPR::ModelParametersLWPR(LWPR_Object* lwpr_object)
:
  lwpr_object_(lwpr_object)
{
  countLengths();
}

void ModelParametersLWPR::countLengths(void)
{
 
  // Determine the lengths of different vectors
  n_centers_ = 0;
  n_slopes_ = 0;
  n_offsets_ = 0;
	for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
	{
		for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
		{
      n_centers_ += lwpr_object_->nIn(); 
      n_slopes_  += lwpr_object_->model.sub[iDim].rf[iRF]->nReg;
      n_offsets_ += 1;
		}
	}
  n_widths_ = n_centers_;
  
}
  
ModelParametersLWPR::~ModelParametersLWPR(void)
{
  delete lwpr_object_;
}

ModelParameters* ModelParametersLWPR::clone(void) const {
  LWPR_Object* lwpr_object_clone = new LWPR_Object(*lwpr_object_);
  return new ModelParametersLWPR(lwpr_object_clone);
}

ostream& ModelParametersLWPR::serialize(ostream& output) const {
  output << "{ \"ModelParametersLWPR\": { \"lwpr_object_xml_string\": \"";

  // Write file
  string filename("/tmp/lpwrfile_serialize.xml");
  lwpr_object_->writeXML(filename.c_str());
  
  // Read file into string stream (through file stream)
  ifstream t(filename);
  stringstream strstream;
  strstream << t.rdbuf(); 

  // Get the string and remove newlines  
  string str = strstream.str();
  str.erase(std::remove(str.begin(), str.end(), '\n'), str.end());
  
  // Output the XML string to the current output stream
  output << str;
  
  output << " \" } }";

  return output;
};


ModelParametersLWPR* ModelParametersLWPR::deserialize(istream& input_stream)
{
  bool remove_white_space = true;
  string json_string = getJSONString(input_stream,remove_white_space);
  
  if (json_string.empty())
    return NULL;
  
  string lwpr_object_xml_string;
  
  lwpr_object_xml_string = getJSONValue(json_string,"lwpr_object_xml_string");
  
  // We now have the LWPR object as an XML string.
  // Save this XML string to a temporary file, and call the LWPR_Object constructor with 
  // the filename. This constructs the LWPR_Object from the XML.
  
  string filename("/tmp/lpwrfile_deserialize.xml");
  ofstream temp(filename);
  temp << lwpr_object_xml_string;
        
  LWPR_Object* lwpr_object = new LWPR_Object(filename.c_str());
  return new ModelParametersLWPR(lwpr_object);

  return NULL;
}

int ModelParametersLWPR::getExpectedInputDim(void) const
{
  return lwpr_object_->nIn();
}

void ModelParametersLWPR::getSelectableParameters(set<string>& selected_values_labels) const 
{
  selected_values_labels = set<string>();
  selected_values_labels.insert("centers");
  selected_values_labels.insert("widths");
  selected_values_labels.insert("slopes");
  selected_values_labels.insert("offsets");
}




void ModelParametersLWPR::getParameterVectorMask(const std::set<std::string> selected_values_labels, VectorXi& selected_mask) const
{
  selected_mask.resize(getParameterVectorAllSize());
  selected_mask.fill(0);
  
  int offset = 0;
  int size;
  
  // Centers
  size = n_centers_;
  if (selected_values_labels.find("centers")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(1);
  offset += size;
  
  // Widths
  size = n_widths_;
  if (selected_values_labels.find("widths")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(2);
  offset += size;
  
  // Offsets
  size = n_offsets_;
  if (selected_values_labels.find("offsets")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(3);
  offset += size;

  // Slopes
  size = n_slopes_;
  if (selected_values_labels.find("slopes")!=selected_values_labels.end())
    selected_mask.segment(offset,size).fill(4);
  offset += size;

  assert(offset == getParameterVectorAllSize());   
}

void ModelParametersLWPR::getParameterVectorAll(VectorXd& values) const
{
  values.resize(getParameterVectorAllSize());
  int ii=0;
  
  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      for (int j = 0; j < lwpr_object_->nIn(); j++)
       values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->c[j];

  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      for (int j = 0; j < lwpr_object_->nIn(); j++)
        values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->D[j*lwpr_object_->model.nInStore+j];

  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      for (int j = 0; j < lwpr_object_->model.sub[iDim].rf[iRF]->nReg; j++)
        values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->beta[j];
      
  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->beta0;
  
  assert(ii == getParameterVectorAllSize()); 
  
};

void ModelParametersLWPR::setParameterVectorAll(const VectorXd& values) {
  if (getParameterVectorAllSize() != values.size())
  {
    cerr << __FILE__ << ":" << __LINE__ << ": values is of wrong size." << endl;
    return;
  }
  
  int ii=0;
  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      for (int j = 0; j < lwpr_object_->nIn(); j++)
      lwpr_object_->model.sub[iDim].rf[iRF]->c[j] = values[ii++];

  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      for (int j = 0; j < lwpr_object_->nIn(); j++)
      lwpr_object_->model.sub[iDim].rf[iRF]->D[j*lwpr_object_->model.nInStore+j] = values[ii++];

  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      for (int j = 0; j < lwpr_object_->model.sub[iDim].rf[iRF]->nReg; j++)
        lwpr_object_->model.sub[iDim].rf[iRF]->beta[j] = values[ii++];

  for (int iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
    for (int iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
      lwpr_object_->model.sub[iDim].rf[iRF]->beta0 = values[ii++];

  assert(ii == getParameterVectorAllSize());   
};

/*
// void FunctionApproximatorLWPR::save(const char* file)
// {
// 	lwpr_object_->writeBinary(file);
// }
*/
