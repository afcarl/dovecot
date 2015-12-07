/**
 * @file   MetaParametersLWPR.h
 * @brief  MetaParametersLWPR class header file.
 * @author Freek Stulp
 */

#ifndef METAPARAMETERSLWPR_H
#define METAPARAMETERSLWPR_H

#include "functionapproximators/MetaParameters.h"

#include <eigen3/Eigen/Core>

/** \brief Meta-parameters for the Locally Weighted Projection Regression (LWPR) function approximator
 * \ingroup FunctionApproximators
 * \ingroup LWPR
 */
class MetaParametersLWPR : public MetaParameters
{
  friend class FunctionApproximatorLWPR;

public:
  
  /** Constructor for the algorithmic meta-parameters of the LWPR function approximator.
   *
   *  The meaning of these parameters is explained here:
   *     http://wcms.inf.ed.ac.uk/ipab/slmc/research/software-lwpr
   *
   *  Short howto:
   *  \li Set update_D=false, diag_only=true, use_meta=false
   *  \li Tune init_D, and then w_gen and w_prune
   *  \li Set update_D=true, then tune init_alpha, then penalty
   *  \li Set diag_only=false, see if it helps, if so re-tune init_alpha if necessary
   *  \li Set use_meta=true, tune meta_rate (I never do this...)  
   *
   *  \param[in] expected_input_dim Expected dimensionality of the input data
   *
   *  \param[in] init_D  Removing/adding kernels: Width of a kernel when it is newly placed. Smaller *                     values mean wider kernels.
   *  \param[in] w_gen   Removing/adding kernels: Threshold for adding a kernel.
   *  \param[in] w_prune Removing/adding kernels: Threshold for pruning a kernel.
   *
   *  \param[in] update_D   Updating existing kernels: whether to update kernels
   *  \param[in] init_alpha Updating existing kernels: rate at which kernels are updated
   *  \param[in] penalty    Updating existing kernels: regularization term. Higher penalty means
   *                        less kernels.
   *  \param[in] diag_only  Whether to update only the diagonal of the covariance matrix of the
   *                        kernel, or the full matrix. 
   * 
   *  \param[in] use_meta    Meta-learning of kernel update rate: whether meta-learning is enabled
   *  \param[in] meta_rate   Meta-learning of kernel update rate: meta-learning rate
   * 
   *  \param[in] kernel_name Removing/adding kernels: Type of kernels
   */
	MetaParametersLWPR(
	  int expected_input_dim,
    Eigen::VectorXd init_D=Eigen::VectorXd::Ones(1),
    double   w_gen=0.2,
    double   w_prune=0.8,
             
    bool     update_D=true,
    double   init_alpha=1.0,
    double   penalty=1.0,
    bool     diag_only=true,
             
    bool     use_meta=false,
    double   meta_rate=1.0,
    std::string   kernel_name=std::string("Gaussian")
  );
		
	MetaParametersLWPR* clone(void) const;
  std::ostream& serialize(std::ostream& output) const;
  
  /** 
   * Deserialize (i.e. read) a MetaParametersLWPR object from an input stream.
   * \param[in] input_stream The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static MetaParametersLWPR* deserialize(std::istream& input_stream);
  
private:
  Eigen::VectorXd init_D_; // If of size 1, call setInitD(double), else setInitD(vector<double>)
  double w_gen_;
  double w_prune_;
    
  bool   update_D_;
  double init_alpha_;
  double penalty_;
  bool   diag_only_;
  
  bool   use_meta_;
  double meta_rate_;
  std::string kernel_name_; // "Gaussian" "BiSquare"

};

#endif        //  #ifndef METAPARAMETERSLWPR_H

