/**
 * @file   ModelParametersGMR.h
 * @brief  ModelParametersGMR class header file.
 * @author Freek Stulp, Thibaut Munzer
 */
 
#ifndef MODELPARAMETERSGMR_H
#define MODELPARAMETERSGMR_H

#include "functionapproximators/ModelParameters.h"

#include <iosfwd>
#include <vector>

/** \brief Model parameters for the GMR function approximator
 * \ingroup FunctionApproximators
 * \ingroup GMR
 */
class ModelParametersGMR : public ModelParameters
{
  friend class FunctionApproximatorGMR;
  
public:
  /** Constructor for the model parameters of the GMR function approximator.
   *  \param[in] centers A list (std::vector) of nb_gaussian center vector (nb_in_dim)
   *  \param[in] priors A list (std::vector) of nb_gaussian prior
   *  \param[in] slopes A list (std::vector) of nb_gaussian associated slope matrix (nb_out_dim x nb_in_dim)
   *  \param[in] biases A list (std::vector) of nb_gaussian associated bias vector (nb_out_dim)
   *  \param[in] inverseCovarsL A list (std::vector) of nb_gaussian matrix. Each matrix is the inverse of the L part of the LLT decomposition of the covariance matrix (nb_in_dim x nb_in_dim)
   */
  ModelParametersGMR(std::vector<Eigen::VectorXd*> centers, std::vector<double*> priors,
    std::vector<Eigen::MatrixXd*> slopes, std::vector<Eigen::VectorXd*> biases,
    std::vector<Eigen::MatrixXd*> inverseCovarsL);
  
	int getExpectedInputDim(void) const;
	
  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a ModelParametersGMR object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static ModelParametersGMR* deserialize(std::istream& input_stream);

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
  std::vector<Eigen::VectorXd*> centers_;
  std::vector<double*>   priors_;
  std::vector<Eigen::MatrixXd*> slopes_;
  std::vector<Eigen::VectorXd*> biases_;
  std::vector<Eigen::MatrixXd*> inverseCovarsL_;

  int nb_in_dim_;

  int  all_values_vector_size_;
};


#endif        //  #ifndef MODELPARAMETERSGMR_H

