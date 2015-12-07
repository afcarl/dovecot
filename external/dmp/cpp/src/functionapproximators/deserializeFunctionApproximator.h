/**
 * @file deserializeFunctionApproximator.h
 * @brief  Header file for function to construct MetaParameters from an input stream.
 * @author Freek Stulp
 *
 */

#ifndef _DESERIALIZE_FUNCTIONAPPROXIMATOR_H_
#define _DESERIALIZE_FUNCTIONAPPROXIMATOR_H_

#include <istream>

// Forward declaration
class MetaParameters;
class ModelParameters;
class FunctionApproximator;

/** 
 * Deserialize MetaParameters from an input stream. 
 * \see page_serialization
 * \param[in] input Input stream from which to deserialize
 * \param[in] meta_parameters MetaParameters to be initialized from stream 
 * \return Input stream from which the MetaParameters object was deserialized
 */
std::istream& operator>>(std::istream& input, MetaParameters*& meta_parameters);

/** 
 * Deserialize ModelParameters from an input stream. 
 * \see page_serialization
 * \param[in] input Input stream from which to deserialize
 * \param[in] model_parameters ModelParameters to be initialized from stream 
 * \return Input stream from which the ModelParameters object was deserialized
 */
std::istream& operator>>(std::istream& input, ModelParameters*& model_parameters);

/** 
 * Deserialize FunctionApproximator from an input stream. 
 * \see page_serialization
 * \param[in] input Input stream from which to deserialize
 * \param[in] function_approximator FunctionApproximator to be initialized from stream 
 * \return Input stream from which the FunctionApproximator object was deserialized
 */
std::istream& operator>>(std::istream& input, FunctionApproximator*& function_approximator);

#endif
