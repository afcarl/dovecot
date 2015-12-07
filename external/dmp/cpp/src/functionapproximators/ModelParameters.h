/**
 * @file   ModelParameters.h
 * @brief  ModelParameters class header file.
 * @author Freek Stulp
 */
 
#ifndef MODELPARAMETERS_H
#define MODELPARAMETERS_H

#include "Parameterizable.h"

#include <iosfwd>
#include <set>
#include <string>


/** \brief Base class for all model parameters of function approximators
 * \ingroup FunctionApproximators
 */
class ModelParameters : public Parameterizable
{
public:

  /** Return a pointer to a deep copy of the ModelParameters object.
   *  \return Pointer to a deep copy
   */
  virtual ModelParameters* clone(void) const = 0;
  
  virtual ~ModelParameters(void) {};

  /** Print to output stream. 
   *
   *  \param[in] output  Output stream to which to write to
   *  \param[in] model_parameters Model-parameters to write
   *  \return    Output stream
   *
   *  \remark Calls virtual function ModelParameters::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const ModelParameters& model_parameters) {
    return model_parameters.serialize(output);
  }
  
 /** Write object to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output stream to which the object was written 
   */
  virtual std::ostream& serialize(std::ostream& output) const = 0;
  
  /** The expected dimensionality of the input data.
   * \return Expected dimensionality of the input data
   */
  virtual int getExpectedInputDim(void) const  = 0;
  
  
public:
  /** Generate a grid of inputs, and output the response of the basis functions and line segments
   * for these inputs.
   * This function is not pure virtual, because this might not make sense for every model parameters
   * class.
   *
   * \param[in] min Minimum values for the grid (one for each dimension)
   * \param[in] max Maximum values for the grid (one for each dimension)
   * \param[in] n_samples_per_dim Number of samples in the grid along each dimension
   * \param[in] directory Directory to which to save the results to.
   * \param[in] overwrite Whether to overwrite existing files. true=do overwrite, false=don't overwrite and give a warning.
   * \return Whether saving the data was successful.
   */
	virtual bool saveGridData(const Eigen::VectorXd& min, const Eigen::VectorXd& max, const Eigen::VectorXi& n_samples_per_dim, std::string directory, bool overwrite=false) const
  {
    return true;
  };
  
};


#endif //  #ifndef MODELPARAMETERS_H

