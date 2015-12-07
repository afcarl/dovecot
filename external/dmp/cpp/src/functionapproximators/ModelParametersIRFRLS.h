/**
 * @file   ModelParametersIRFRLS.h
 * @brief  ModelParametersIRFRLS class header file.
 * @author Freek Stulp, Thibaut Munzer
 */
 
#ifndef MODELPARAMETERSIRFRLS_H
#define MODELPARAMETERSIRFRLS_H

#include <iosfwd>

#include "functionapproximators/ModelParameters.h"

/** \brief Model parameters for the iRFRLS function approximator
 * \ingroup FunctionApproximators
 * \ingroup IRFRLS
 */
class ModelParametersIRFRLS : public ModelParameters
{
  friend class FunctionApproximatorIRFRLS;
  
public:
  /** Constructor for the model parameters of the IRFRLS function approximator.
   *  \param[in] linear_models Coefficient of the linear models (nb_cos x nb_out_dim).
   *  \param[in] cosines_periodes Matrix of periode for each cosine for each input dimension (nb_cos x nb_in_dim). 
   *  \param[in] cosines_phase Vector of periode (nb_cos).
   */
  ModelParametersIRFRLS(Eigen::MatrixXd linear_models, Eigen::MatrixXd cosines_periodes, Eigen::VectorXd cosines_phase);
	
	int getExpectedInputDim(void) const;
	
  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a ModelParametersIRFRLS object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static ModelParametersIRFRLS* deserialize(std::istream& input_stream);

  ModelParameters* clone(void) const;

  void getSelectableParameters(std::set<std::string>& selected_values_labels) const;
  void getParameterVectorMask(const std::set<std::string> selected_values_labels, Eigen::VectorXi& selected_mask) const;
  void getParameterVectorAll(Eigen::VectorXd& all_values) const;
  
  inline int getParameterVectorAllSize(void) const
  {
    return all_values_vector_size_;
  }

protected:
  void setParameterVectorAll(const Eigen::VectorXd& values);
  
private:
  
  Eigen::MatrixXd linear_models_;
  Eigen::MatrixXd cosines_periodes_;
  Eigen::VectorXd cosines_phase_;

  int nb_in_dim_;

  int  all_values_vector_size_;
};


#endif        //  #ifndef MODELPARAMETERSIRFRLS_H

