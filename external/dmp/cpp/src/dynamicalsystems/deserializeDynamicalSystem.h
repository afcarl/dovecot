/**
 * @file deserializeDynamicalSystem.h
 * @brief  Header file for function to construct a Dynamical System from an input stream.
 * @author Freek Stulp
 *
 */

#ifndef _DESERIALIZE_DYNAMICAL_SYSTEM_H_
#define _DESERIALIZE_DYNAMICAL_SYSTEM_H_

#include <istream>

// Forward declaration
class DynamicalSystem;

/**
 * \page page_serialization Serialization
Since C++ doesn't have reflection (or an eval function, thank goodness), initializing objects from strings or streams is tricky. You have to know the class before you can call the appropriate method to parse the string, but you don't know the class until you've parsed the string. Bummer.

Options:

\li Use some external library like boost to do the job of deserialization. I considered using the boost::property_tree for this, but it has a messy way to store arrays in JSON. Since we will be storing many arrays (i.e. Eigen vectors and matrices) I decided against this. Direct serialization with boost is possible, but it is messy when exchanging data with Matlab: https://groups.google.com/forum/#!topic/boost-list/9OHUsTsPBRk

\li Use the Registry pattern: http://securesoftwaredev.com/2009/03/01/the-registry-pattern/ However, there are some disadvantages to this also (described starting at ~9 minutes here http://www.youtube.com/watch?v=RlfLCWKxHJ0, they call the pattern a Service Locator). Also, I thought this would simply be overkill for this application.

\li Make a function that knows about all possible subclasses, and can thus choose the right constructor. Disadvantage: subclasses cannot be added on the fly, but must be included in this function (i.e. their headers must be included in the cpp file that implements the 'constructor chooser'). Advantage: easy to understand, easy to implement, no dependencies on external libraries. For those reasons, that is the option I chose, and deserializeDynamicalSystem() is that function.

If you know a easier/better light-weight way to do this, please let me know.
*/

/** 
 * Deserialize a DynamicalSystem from an input stream. 
 * \see page_serialization
 * \param[in] input Input stream from which to deserialize from
 * \return Pointer to a dynamical system
 */
DynamicalSystem* deserializeDynamicalSystem(std::istream &input);

/** 
 * Deserialize DynamicalSystem from an input stream. 
 * \see page_serialization
 * \param[in] input Input stream from which to deserialize
 * \param[in] dyn_sys DynamicalSystem to be initialized from stream 
 * \return Input stream from which the DynamicalSystem object was deserialized
 */
std::istream& operator>>(std::istream& input, DynamicalSystem*& dyn_sys);

#endif
