/**
 * @file   MetaParametersLWR.h
 * @brief  MetaParametersLWR class header file.
 * @author Freek Stulp
 */
 
#ifndef METAPARAMETERSLWR_H
#define METAPARAMETERSLWR_H

#include "functionapproximators/MetaParameters.h"

#include <iosfwd>
#include <vector>
#include <eigen3/Eigen/Core>

/** \brief Meta-parameters for the Locally Weighted Regression (LWR) function approximator
 * \ingroup FunctionApproximators
 * \ingroup LWR
 */
class MetaParametersLWR : public MetaParameters
{
  
public:
  
  /** Constructor for the algorithmic meta-parameters of the LWR function approximator.
   *  \param[in] expected_input_dim         The dimensionality of the data this function approximator expects. Although this information is already contained in the 'centers_per_dim' argument, we ask the user to pass it explicitely so that various checks on the arguments may be conducted.
   *  \param[in] centers_per_dim Centers of the basis functions, one VectorXd for each dimension.
   *  \param[in] overlap Overlap between the basis functions. If the distance between the centers of two adjacent basis functions is 'dist', then the sigma of the Gaussian kernel is overlap*dist 
   */
   MetaParametersLWR(int expected_input_dim, const std::vector<Eigen::VectorXd>& centers_per_dim, double overlap=0.1);
		 
  /** Constructor for the algorithmic meta-parameters of the LWR function approximator.
   *  \param[in] expected_input_dim         The dimensionality of the data this function approximator expects. Although this information is already contained in the 'centers' argument, we ask the user to pass it explicitely so that various checks on the arguments may be conducted.
   *  \param[in] n_basis_functions_per_dim  Number of basis functions
   *  \param[in] overlap                    Overlap of a basis function with its neighbors
   *
   *  The centers and widths of the basis functions are determined from these parameters once the
   *  range of the input data is known, see also setInputMinMax()
   */
  MetaParametersLWR(int expected_input_dim, const Eigen::VectorXi& n_basis_functions_per_dim, double overlap=0.1);
  
  
  /** Constructor for the algorithmic meta-parameters of the LWR function approximator.
   * This is for the special case when the dimensionality of the input data is 1.
   *  \param[in] expected_input_dim         The dimensionality of the data this function approximator expects. Since this constructor is for 1-D input data only, we simply check if this argument is equal to 1.
   *  \param[in] n_basis_functions  Number of basis functions for the one dimension
   *  \param[in] overlap            Overlap of a basis function with its neighbors
   *
   *  The centers and widths of the basis functions are determined from these parameters once the
   *  range of the input data is known, see also setInputMinMax()
   */
	MetaParametersLWR(int expected_input_dim, int n_basis_functions=10, double overlap=0.1);

	/** Get the centers and widths of the basis functions.
	 *  \param[in] min Minimum values of input data (one value for each dimension).
	 *  \param[in] max Maximum values of input data (one value for each dimension).
	 *  \param[out] centers Centers of the basis functions (matrix of size n_basis_functions X n_input_dims
	 *  \param[out] widths Widths of the basis functions (matrix of size n_basis_functions X n_input_dims
	 *
	 * The reason why there are not two functions getCenters and getWidths is that it is much easier
	 * to compute both at the same time, and usually you will need both at the same time anyway.
	 */
	void getCentersAndWidths(const Eigen::VectorXd& min, const Eigen::VectorXd& max, Eigen::MatrixXd& centers, Eigen::MatrixXd& widths) const;
	

	MetaParametersLWR* clone(void) const;

  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a MetaParametersLWR object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static MetaParametersLWR* deserialize(std::istream& input_stream);

private:
  const Eigen::VectorXi n_bfs_per_dim_;
  const std::vector<Eigen::VectorXd> centers_per_dim_;
  const double overlap_;

};


#endif        //  #ifndef METAPARAMETERSLWR_H

