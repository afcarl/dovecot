/**
 * @file   MetaParameters.h
 * @brief  MetaParameters class header file.
 * @author Freek Stulp
 */
 
#ifndef METAPARAMETERS_H
#define METAPARAMETERS_H

#include <iosfwd>

/** \brief Base class for all meta-parameters of function approximators
 * \ingroup FunctionApproximators
 */
class MetaParameters
{
public:
  /** Constructor.
   *  \param[in] expected_input_dim Expected dimensionality of the input data
   */
	MetaParameters(int expected_input_dim);
	
  /** Return a pointer to a deep copy of the MetaParameters object.
   *  \return Pointer to a deep copy
   */
	virtual MetaParameters* clone(void) const = 0;
	
  /** The expected dimensionality of the input data.
   * \return Expected dimensionality of the input data
   */
  int getExpectedInputDim(void) const
  { 
    return expected_input_dim_;  
  }
  
  /** Write MetaParameters to output stream. 
   *  \param[in] output Output stream to which to write to
   * \return Output stream to which data was written
   */
  virtual std::ostream& serialize(std::ostream& output) const = 0;

  /** Print to output stream. 
   *
   *  \param[in] output  Output stream to which to write to
   *  \param[in] meta_parameters Meta-parameters to write
   *  \return    Output stream
   *
   *  \remark Calls virtual function MetaParameters::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const MetaParameters& meta_parameters);
  
private:
  int expected_input_dim_;  

};


#endif //  #ifndef METAPARAMETERS_H

