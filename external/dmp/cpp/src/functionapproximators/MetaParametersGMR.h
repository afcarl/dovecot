/**
 * @file   MetaParametersGMR.h
 * @brief  MetaParametersGMR class header file.
 * @author Freek Stulp, Thibaut Munzer
 */

#ifndef METAPARAMETERSGMR_H
#define METAPARAMETERSGMR_H

#include "functionapproximators/MetaParameters.h"

/** \brief Meta-parameters for the GMR function approximator
 * \ingroup FunctionApproximators
 * \ingroup GMR
 */
class MetaParametersGMR : public MetaParameters
{
  friend class FunctionApproximatorGMR;
  
public:

  /** Constructor for the algorithmic meta-parameters of the GMR function approximator
   *  \param[in] expected_input_dim Expected dimensionality of the input data
   *  \param[in] number_of_gaussians Number of gaussians
   */
	MetaParametersGMR(int expected_input_dim, int number_of_gaussians);
	
	MetaParametersGMR* clone(void) const;

  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a MetaParametersGMR object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static MetaParametersGMR* deserialize(std::istream& input_stream);
  
private:
  /** Number of gaussians */
  int number_of_gaussians_;
};


#endif        //  #ifndef METAPARAMETERSGMR_H

