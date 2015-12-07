/**
 * @file   MetaParametersIRFRLS.h
 * @brief  MetaParametersIRFRLS class header file.
 * @author Freek Stulp, Thibaut Munzer
 */

#ifndef METAPARAMETERSIRFRLS_H
#define METAPARAMETERSIRFRLS_H

#include "functionapproximators/MetaParameters.h"

#include <iosfwd>

/** \brief Meta-parameters for the iRFRLS function approximator
 * \ingroup FunctionApproximators
 * \ingroup IRFRLS
 */
 class MetaParametersIRFRLS : public MetaParameters
{
  friend class FunctionApproximatorIRFRLS;
  
public:

  /** Constructor for the algorithmic meta-parameters of the IRFRLS function approximator
   *  \param[in] expected_input_dim Expected dimensionality of the input data
   *  \param[in] number_of_basis_functions Number of basis functions
   *  \param[in] lambda Ridge regression coefficient, tradeoff between data fit and model complexity
   *  \param[in] gamma Cosines periodes distribution standard derivation
   */
	MetaParametersIRFRLS(int expected_input_dim, int number_of_basis_functions, double lambda, double gamma);
	
	MetaParametersIRFRLS* clone(void) const;
	
  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a MetaParametersIRFRLS object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
	static MetaParametersIRFRLS* deserialize(std::istream& input_stream);

private:

  /** Number of basis functions */
  int number_of_basis_functions_;

  /** Ridge regression coefficient, tradeoff between data fit and model complexity */
  double lambda_;

  /** Cosines periodes distribution standard derivation */
  double gamma_;

};


#endif        //  #ifndef METAPARAMETERSIRFRLS_H

