/**
 * @file   ModelParametersLWR.h
 * @brief  ModelParametersLWR class header file.
 * @author Freek Stulp
 */
 
#ifndef MODELPARAMETERSLWR_H
#define MODELPARAMETERSLWR_H

#include <iosfwd>
#include <vector>
#include <eigen3/Eigen/Core>

#include "functionapproximators/ModelParameters.h"

/** \brief Model parameters for the Locally Weighted Regression (LWR) function approximator
 * \ingroup FunctionApproximators
 * \ingroup LWR
 */
class ModelParametersLWR : public ModelParameters
{
  friend class FunctionApproximatorLWR;
  
public:
  /** Constructor for the model parameters of the LWPR function approximator.
   *  \param[in] centers Centers of the basis functions
   *  \param[in] widths  Widths of the basis functions. 
   *  \param[in] slopes  Slopes of the line segments. 
   *  \param[in] offsets Offsets of the line segments, i.e. the value of the line segment at its intersection with the y-axis.
   */
  ModelParametersLWR(const Eigen::MatrixXd& centers, const Eigen::MatrixXd& widths, const Eigen::MatrixXd& slopes, const Eigen::MatrixXd& offsets);
  
  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a ModelParametersLWR object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static ModelParametersLWR* deserialize(std::istream& input_stream);
  
	ModelParameters* clone(void) const;
	
  int getExpectedInputDim(void) const  {
    return centers_.cols();
  };
  
  /** Get the activation of one kernel for given centers, widths and inputs
   * \param[in] center The center of the basis function (size: 1 X n_dims)
   * \param[in] width The width of the basis function (size: 1 X n_dims)
   * \param[in] inputs The input data (size: n_samples X n_dims)
   * \param[out] kernel_activations The kernel activations, computed for each of the sampels in the input data (size: n_samples X 1)
   */
  static void kernelActivations(const Eigen::VectorXd& center, const Eigen::VectorXd& width, const Eigen::MatrixXd& inputs, Eigen::Ref<Eigen::VectorXd> kernel_activations);
  
  /** Get the normalized kernel activations for given centers, widths and inputs
   * \param[in] centers The centers of the basis functions (size: n_basis_functions X n_dims)
   * \param[in] widths The widths of the basis functions (size: n_basis_functions X n_dims)
   * \param[in] inputs The input data (size: n_samples X n_dims)
   * \param[out] normalized_kernel_activations The normalized kernel activations, computed for each of the sampels in the input data (size: n_samples X n_basis_functions)
   */
  static void normalizedKernelActivations(const Eigen::MatrixXd& centers, const Eigen::MatrixXd& widths, const Eigen::MatrixXd& inputs, Eigen::MatrixXd& normalized_kernel_activations);
	
  /** Get the normalized kernel activations for given inputs
   * \param[in] inputs The input data (size: n_samples X n_dims)
   * \param[out] normalized_kernel_activations The normalized kernel activations, computed for each of the sampels in the input data (size: n_samples X n_basis_functions)
   */
  void normalizedKernelActivations(const Eigen::MatrixXd& inputs, Eigen::MatrixXd& normalized_kernel_activations) const;
  
  /** Get the output of each linear model (unweighted) for the given inputs.
   * \param[in] inputs The inputs for which to compute the output of the lines models (size: n_samples X  n_input_dims)
   * \param[out] lines The output of the linear models (size: n_samples X n_output_dim) 
   */
  void getLines(const Eigen::MatrixXd& inputs, Eigen::MatrixXd& lines) const;
  
  /** Compute the sum of the locally weighted lines. 
   * \param[in] inputs The inputs for which to compute the output (size: n_samples X  n_input_dims)
   * \param[out] output The weighted linear models (size: n_samples X n_output_dim) 
   *
   */
  void locallyWeightedLines(const Eigen::MatrixXd& inputs, Eigen::MatrixXd& output) const;
  
  void setParameterVectorModifierPrivate(std::string modifier, bool new_value);
  
  /** Set whether the offsets should be adapted so that the line segments pivot around the mode of
   * the basis function, rather than the intersection with the y-axis.
   * \param[in] lines_pivot_at_max_activation Whether to pivot around the mode or not.
   *
   */
  void set_lines_pivot_at_max_activation(bool lines_pivot_at_max_activation);

  /** Whether to return slopes as angles or slopes in ModelParametersLWR::getParameterVectorAll()
   * \param[in] slopes_as_angles Whether to return as slopes (true) or angles (false)
   * \todo Implement and document
   */
  void set_slopes_as_angles(bool slopes_as_angles);
  
  void getSelectableParameters(std::set<std::string>& selected_values_labels) const;
  void getParameterVectorMask(const std::set<std::string> selected_values_labels, Eigen::VectorXi& selected_mask) const;
  void getParameterVectorAll(Eigen::VectorXd& all_values) const;
  inline int getParameterVectorAllSize(void) const
  {
    return all_values_vector_size_;
  }
  
	bool saveGridData(const Eigen::VectorXd& min, const Eigen::VectorXd& max, const Eigen::VectorXi& n_samples_per_dim, std::string directory, bool overwrite=false) const;

protected:
  void setParameterVectorAll(const Eigen::VectorXd& values);
  
private:
  Eigen::MatrixXd centers_; // n_centers X n_dims
  Eigen::MatrixXd widths_;  // n_centers X n_dims
  Eigen::MatrixXd slopes_;  // n_centers X n_dims
  Eigen::VectorXd offsets_; //         1 X n_dims

  bool lines_pivot_at_max_activation_;
  bool slopes_as_angles_;
  int  all_values_vector_size_;

public:
	/** Turn caching for the function normalizedKernelActivations() on or off.
	 * Turning this on should lead to substantial improvements in execution time if the centers and
	 * widths of the kernels do not change often AND you call normalizedKernelActivations with the
	 * same inputs over and over again.
	 * \param[in] caching Whether to turn caching on or off
	 * \remarks In the constructor, caching is set to true, so by default it is on.
	 */
	inline void set_caching(bool caching)
	{
	  caching_ = caching;
	  if (!caching_) clearCache();
	}
	
private:
  mutable Eigen::MatrixXd inputs_cached_;
  mutable Eigen::MatrixXd normalized_kernel_activations_cached_;
  bool caching_;
  inline void clearCache(void) 
  {
    inputs_cached_.resize(0,0);
    normalized_kernel_activations_cached_.resize(0,0);
  }
};


#endif        //  #ifndef MODELPARAMETERSLWR_H

