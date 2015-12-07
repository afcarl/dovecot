/**
 * @file   FunctionApproximator.h
 * @brief  FunctionApproximator class header file.
 * @author Freek Stulp
 */

/** \defgroup FunctionApproximators Function Approximators
 */

#ifndef _FUNCTIONAPPROXIMATOR_H_
#define _FUNCTIONAPPROXIMATOR_H_

#include "Parameterizable.h"

#include <string>
#include <vector>
#include <eigen3/Eigen/Core>

// Forward declarations
class MetaParameters;
class ModelParameters;

/** \brief Base class for all function approximators.
 *  \ingroup FunctionApproximators
 */
class FunctionApproximator : public Parameterizable
{

public:
  
  /** Initialize a function approximator with meta- and optionally model-parameters
   *  \param[in] meta_parameters  The training algorithm meta-parameters
   *  \param[in] model_parameters The parameters of the trained model. If this parameter is not
   *                              passed, the function approximator is initialized as untrained. 
   *                              In this case, you must call FunctionApproximator::train() before
   *                              being able to call FunctionApproximator::predict().
   */
  FunctionApproximator(MetaParameters *meta_parameters, ModelParameters *model_parameters=NULL);
  
  /** Initialize a function approximator with model-parameters
   *  \param[in] model_parameters The parameters of the trained model.
   */
  FunctionApproximator(ModelParameters *model_parameters);

  virtual ~FunctionApproximator(void);
  
  /** Return a pointer to a deep copy of the FunctionApproximator object.
   *  \return Pointer to a deep copy
   */
  virtual FunctionApproximator* clone(void) const = 0;
  
  /** Train the function approximator with corresponding input and target examples.
   *  \param[in] inputs  Input values of the training examples
   *  \param[in] targets Target values of the training examples
   */
  virtual void train(const Eigen::MatrixXd& inputs, const Eigen::MatrixXd& targets) = 0;
  
  /** Train the function approximator with corresponding input and target examples (and write results to file).
   *  \param[in] inputs  Input values of the training examples
   *  \param[in] targets Target values of the training examples
   *  \param[in] save_directory Directory to which to write results.
   * \param[in] overwrite Whether to overwrite existing files. true=do overwrite, false=don't overwrite and give a warning.
   */
  void train(const Eigen::MatrixXd& inputs, const Eigen::MatrixXd& targets, std::string save_directory, bool overwrite=false);

  /** Re-train the function approximator with corresponding input and target examples.
   *  \param[in] inputs  Input values of the training examples
   *  \param[in] targets Target values of the training examples
   *  Re-training could in principle have been enabled through FunctionApproximator::train, but we
   *  wanted to keep a clear disctinction between training (which must be done at least once before 
   *  FunctionApproximator::predict) can be called and re-training.
   */
  void reTrain(const Eigen::MatrixXd& inputs, const Eigen::MatrixXd& targets);
  
  /** Re-train the function approximator with corresponding input and target examples (and write results to file).
   *  \param[in] inputs  Input values of the training examples
   *  \param[in] targets Target values of the training examples
   *  \param[in] save_directory Directory to which to write results.
   * \param[in] overwrite Overwrite existing files in the directory above (default: false)
   *  Re-training could in principle have been enabled through FunctionApproximator::train, but we
   *  wanted to keep a clear disctinction between training (which must be done at least once before 
   *  FunctionApproximator::predict) can be called and re-training.
   */
  void reTrain(const Eigen::MatrixXd& inputs, const Eigen::MatrixXd& targets, std::string save_directory, bool overwrite=false);
  
  /** Query the function approximator to make a prediction
   *  \param[in]  inputs   Input values of the query
   *  \param[out] outputs  Predicted output values
   *
   * \remark This method should be const. But third party functions which is called in this function
   * have not always been implemented as const (Examples: LWPRObject::predict or IRFRLS::predict ).
   * Therefore, this function cannot be const.
   */
  virtual void predict(const Eigen::MatrixXd& inputs, Eigen::MatrixXd& outputs) = 0;
  
  /** Determine whether the function approximator has already been trained with data or not.
   *  \return true if the function approximator has already been trained, false otherwise.
   */
  bool isTrained(void) const
  {
    return (model_parameters_!=NULL);
  }
  
  /** The expected dimensionality of the input data.
   * \return Expected dimensionality of the input data
   */
  int getExpectedInputDim(void) const;
  
  /** The expected dimensionality of the output data.
   * For now, we only consider 1-dimensional output.
   * \return Expected dimensionality of the output data
   */
  int getOutputDim(void) const 
  {
    return 1;
  }
  
  /** Get the name of this function approximator
   *  \return Name of this function approximator
   */
  virtual std::string getName(void) const = 0;
  
  void getSelectableParameters(std::set<std::string>& selected_values_labels) const;
  void setSelectedParameters(const std::set<std::string>& selected_values_labels);
  void getParameterVectorSelectedMinMax(Eigen::VectorXd& min, Eigen::VectorXd& max) const;
  int getParameterVectorSelectedSize(void) const;
  void setParameterVectorSelected(const Eigen::VectorXd& values, bool normalized=false);
  void getParameterVectorSelected(Eigen::VectorXd& values, bool normalized=false) const;

  void getParameterVectorMask(const std::set<std::string> selected_values_labels, Eigen::VectorXi& selected_mask) const;
  int getParameterVectorAllSize(void) const;
  void getParameterVectorAll(Eigen::VectorXd& values) const;
  void setParameterVectorAll(const Eigen::VectorXd& values);


  
  /** Print to output stream. 
   *
   *  \param[in] output  Output stream to which to write to
   *  \param[in] function_approximator Function approximator to write
   *  \return    Output stream
   *
   *  \remark Calls virtual function FunctionApproximator::serialize, which must be implemented by
   * subclasses: http://stackoverflow.com/questions/4571611/virtual-operator
   */ 
  friend std::ostream& operator<<(std::ostream& output, const FunctionApproximator& function_approximator) {
    return function_approximator.serialize(output);
  }
  
  /** Writes the object to an output stream.
   *  \param[in] output The output stream to which to write to.
   *  \return    Output stream
   */
  std::ostream& serialize(std::ostream& output) const;
  
  
  /** Accessor for FunctionApproximator::meta_parameters_
   *  \return The meta-parameters of the algorithm
   */
  const MetaParameters* getMetaParameters(void) const;
  
  /** Accessor for FunctionApproximator::model_parameters_
   *  \return The model parameters of the trained model
   */
  const ModelParameters* getModelParameters(void) const;
  
  void setParameterVectorModifierPrivate(std::string modifier, bool new_value);
  
protected:

  /** Accessor for FunctionApproximator::model_parameters_
   *  \param[in] model_parameters The model parameters of a trained model
   */
  void setModelParameters(ModelParameters* model_parameters);
  
private:
  
  /** The meta-parameters of the function approximator.
   *
   *  These are all the algorithmic parameters that are used when training the function 
   *  approximator. These are thus only used in the FunctionApproximator::train function.
   */
  MetaParameters*  meta_parameters_;
  
  /** The model parameters of the function approximator.
   *
   *  These are all the parameters of a trained function approximator. These are determined when 
   *  training the function approximator in FunctionApproximator::train, and used to make
   *  predictions in FunctionApproximator::predict.
   */
  ModelParameters* model_parameters_;
  
  bool checkModelParametersInitialized(void) const;
  
};


#endif // _FUNCTIONAPPROXIMATOR_H_

/** \page page_func_approx Function Approximation Module

\section sec_fa Function Approximation

This module implements a set of function approximators, i.e. supervised learning algorithms that are trained with demonstration pairs input/target, after which they make predictions for new inputs. For simplicity, this module implements only batch learning (not incremental), and does not allow trained function approximators to be retrained.

The two main functions are FunctionApproximator::train, which takes a set of inputs and corresponding targets, and FunctionApproximator::predict, which makes predictions for novel inputs. 

\subsection sec_fa_metaparameters MetaParameters and ModelParameters

In this module, algorithmic parameters are called MetaParameters, and the parameters of the model when the function approximator has been trained are called ModelParameters. The rationale for this is that an untrained function approximator can be entirely reconstructed if its MetaParameters are known; this is useful for saving to file and making copies. A trained function approximator can be compeletely reconstructed given only its ModelParameters.

The life-cycle of a function approximator is as follows:

\b 1. \b Initialization: The function approximator is initialized by calling the constructor with the MetaParameters. Its ModelParameters are set to NULL, indicating that the model is untrained.

\b 2. \b Training: FunctionApproximator::train is called, which performs the conversion: \f$ \mbox{train}: \mbox{MetaParameters} \times \mbox{Inputs} \times \mbox{Targets} \mapsto \mbox{ModelParameters} \f$

\b 3. \b Prediction: FunctionApproximator::predict is called, which performs the conversion: \f$ \mbox{predict}: \mbox{ModelParameters} \times \mbox{Input} \mapsto \mbox{Output}\f$

\em Remark. FunctionApproximator::train in Step \b 2. may only be called once. If you explicitely want to retrain the function approximator with novel input/target data call FunctionApproximator::reTrain() instead.

\em Remark. During the initialization, ModelParameters may also be passed to the constructor. This means that an already trained function approximator is initialized. Step \b 2. above is thus skipped.

\subsection sec_fa_changing_modelparameters Changing the ModelParameters of a FunctionApproximator

The user should not be allowed to set the ModelParameters of a trained function approximator directly. Hence, FunctionApproximator::setModelParameters is protected. However, in order to change the values inside the model parameters (for instance when optimizing them), the user may call ModelParameters::getParameterVectorSelected and ModelParameters::setParameterVectorSelected it inherits these functions from Parameterizable). These take a vector of doubles, check if the vector has the right size, and get/set the ModelParameters accordingly.

Function approximators often have different types of model parameters. For instance, the model parameters of Locally Weighted Regression (FunctionApproximatorLWR) represent the centers and widths of the basis functions, as well as the slopes of the line segments. If you only want to get/set the slopes when calling ModelParameters::getParameterVectorSelected and ModelParameters::setParameterVectorSelected, you must use ModelParameters::setSelectedParameters(const std::set<std::string>& selected_values_labels), for instance as follows:

\code
std::set<std::string> selected;
selected.insert("slopes");
model_parameters.setSelectedParameters(selected);
Eigen::VectorXd values;
model_parameters.getParameterVectorSelected(values);
// "values" now only contains the slopes of the line segments

selected.clear();
selected.insert("centers");
selected.insert("slopes");
model_parameters.setSelectedParameters(selected);
model_parameters.getParameterVectorSelected(values);
// "values" now contains the centers of the basis functions AND slopes of the line segments

\endcode

The rationale behind this implementation is that optimizers (such as evolution strategies) should not have to care about whether a particular set of model parameters contains centers, widths or slopes. Therefore, these different types of parameters are provided in one vector without semantics, and the generic interface is provided by the Parameterizable class.

Classes that inherit from Parameterizable (such as all ModelParameters and FunctionApproximator subclasses, must implement the pure virtual methods Parameterizable::getParameterVectorAll Parameterizable::setParameterVectorAll and Parameterizable::getParameterVectorMask. Which gets/sets all the possible parameters in one vector, and a mask specifying the semantics of each value in the vector. The work of setting/getting the selected parameters (and normalizing them) is done in the Parameterizable class itself. This approach is a slightly longer run-time than doing the work in the subclasses, but it leads to more legible and robust code (less code duplication).
 */
