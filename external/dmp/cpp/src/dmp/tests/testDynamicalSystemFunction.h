/**
 * @file testDynamicalSystemFunction.h
 * @brief  Header file for function to test a Dynamical System.
 * @author Freek Stulp
 *
 */

#ifndef _TEST_DYNAMICAL_SYSTEM_FUNCTION_H_
#define _TEST_DYNAMICAL_SYSTEM_FUNCTION_H_

#include <string>

// Forward declaration
class DynamicalSystem;

/** Function to test a dynamical system, i.e. do numerical integration, compute the analytical
 *  solution, save results to file, etc.
 *
 * \param[in] dyn_sys The dynamical system to test
 * \param[in] dt      Integration constant
 * \param[in] T       Number of integration steps
 * \param[in] output_analytical_filename Name of output file for analytical data (optional)
 * \param[in] output_step_filename Name of output file for numerical integration data (optional)
 */
void testDynamicalSystemFunction(DynamicalSystem* dyn_sys, double dt, int T, std::string directory="");

#endif


