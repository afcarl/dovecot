/**
 * @file   ModelParametersLWPR.h
 * @brief  ModelParametersLWPR class header file.
 * @author Freek Stulp
 */
 

#ifndef MODELPARAMETERSLWPR_H
#define MODELPARAMETERSLWPR_H

#include <iosfwd>

#include "functionapproximators/ModelParameters.h"

// Forward declarations
class LWPR_Object;

/** \brief Model parameters for the Locally Weighted Projection Regression (LWPR) function approximator
 * \ingroup FunctionApproximators
 * \ingroup LWPR
 */
class ModelParametersLWPR : public ModelParameters
{
  friend class FunctionApproximatorLWPR;
  
public:
  /** Initializing constructor.
   *
   *  Initialize the LWPR model parameters with an LWPR object from the external library.
   *
   *  \param[in] lwpr_object LWPR object from the external library
   */
	ModelParametersLWPR(LWPR_Object* lwpr_object);
	
	~ModelParametersLWPR(void);

  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a ModelParametersLWPR object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static ModelParametersLWPR* deserialize(std::istream& input_stream);

  ModelParameters* clone(void) const;

  int getExpectedInputDim(void) const;
  
  void getSelectableParameters(std::set<std::string>& selected_values_labels) const;
  void getParameterVectorMask(const std::set<std::string> selected_values_labels, Eigen::VectorXi& selected_mask) const;
  void getParameterVectorAll(Eigen::VectorXd& all_values) const;
  
  inline int getParameterVectorAllSize(void) const
  {
    return  n_centers_ + n_widths_ + n_slopes_ + n_offsets_;
  }
  

protected:
  void setParameterVectorAll(const Eigen::VectorXd& values);
  
private:
  LWPR_Object* lwpr_object_;
  
  void countLengths(void);
  int n_centers_;
  int n_widths_;
  int n_slopes_;
  int n_offsets_;

};


#endif        //  #ifndef MODELPARAMETERSLWPR_H

