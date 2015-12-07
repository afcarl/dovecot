/**
 * @file ExponentialSystem.h
 * @brief  ExponentialSystem class header file.
 * @author Freek Stulp
 */

#ifndef _EXPONENTIAL_SYSTEM_H_
#define _EXPONENTIAL_SYSTEM_H_

#include "dynamicalsystems/DynamicalSystem.h"

#include <iostream>

/** \brief Dynamical System modelling the evolution of an exponential system: \f$\dot{x} = -\alpha (x-x^g)\f$.
 * 
 * http://en.wikipedia.org/wiki/Exponential_decay
 *
 * http://en.wikipedia.org/wiki/Exponential_growth 
 *
 * \ingroup DynamicalSystems
 */
class ExponentialSystem : public DynamicalSystem
{
public:

  /**
   *  Initialization constructor.
   *  \param tau     Time constant, cf. DynamicalSystem::tau()
   *  \param y_init  Initial state, cf. DynamicalSystem::initial_state()
   *  \param y_attr  Attractor state, cf. DynamicalSystem::attractor_state()
   *  \param alpha   Decay constant, cf. ExponentialSystem::alpha()
   *  \param name    Name for the sytem, cf. DynamicalSystem::name()     
   */
   ExponentialSystem(double tau, Eigen::VectorXd y_init, Eigen::VectorXd y_attr, double alpha, std::string name="ExponentialSystem");
  
  /** Destructor. */
  ~ExponentialSystem(void);
  
  DynamicalSystem* clone(void) const;
  
  void differentialEquation(const Eigen::VectorXd& x, Eigen::Ref<Eigen::VectorXd> xd) const;  
  
  void analyticalSolution(const Eigen::VectorXd& ts, Eigen::MatrixXd& xs, Eigen::MatrixXd& xds) const;
  
  std::ostream& serialize(std::ostream& output) const;

  /** 
   * Deserialize (i.e. read) a dynamical system from an input stream.
   * \param[in] input The input stream (which will be modified due to reading from it)
   * \return A pointer to a new dynamical system that was read from the input stream
   */
  static DynamicalSystem* deserialize(std::istream& input);

private:
  
  /** Decay constant */
  double alpha_;
  
};



#endif // _Exponential_SYSTEM_H_

