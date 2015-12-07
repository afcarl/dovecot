/**
 * @file SpringDamperSystem.h
 * @brief  SpringDamperSystem class header file.
 * @author Freek Stulp
 */

#ifndef _SPRING_DAMPER_SYSTEM_H_
#define _SPRING_DAMPER_SYSTEM_H_

#include "dynamicalsystems/DynamicalSystem.h"

/** Value indicating that the spring constant should be set such that the
 *  spring damper system is critically damped.
 */
double const CRITICALLY_DAMPED = -1.0;

/** \brief Dynamical System modelling the evolution of a spring-damper system: \f$ m\ddot{x} = -k(x-x^g) -c\dot{x}\f$.
 * 
 * http://en.wikipedia.org/wiki/Damped_spring-mass_system
 *
 * \ingroup DynamicalSystems
 */
class SpringDamperSystem : public DynamicalSystem
{
public:
  
  /**
   *  Initialization constructor.
   *  \param tau     Time constant,            cf. DynamicalSystem::tau()
   *  \param y_init  Initial state,            cf. DynamicalSystem::initial_state()
   *  \param y_attr  Attractor state,          cf. DynamicalSystem::attractor_state()
   *  \param spring_constant  Spring constant, cf. SpringDamperSystem::spring_constant()
   *  \param damping_coefficient  Damping coefficient, cf. SpringDamperSystem::damping_coefficient()
   *  \param mass    Mass,                     cf. SpringDamperSystem::mass()
   *  \param name    Name for the sytem,       cf. DynamicalSystem::name()
   */
  SpringDamperSystem(double tau, Eigen::VectorXd y_init, Eigen::VectorXd y_attr, 
    double damping_coefficient, double spring_constant=CRITICALLY_DAMPED, double mass=1.0, std::string name="SpringDamperSystem");
    
  /** Destructor. */
  ~SpringDamperSystem(void);

  DynamicalSystem* clone(void) const;

  void differentialEquation(const Eigen::VectorXd& x, Eigen::Ref<Eigen::VectorXd> xd) const;

  void analyticalSolution(const Eigen::VectorXd& ts, Eigen::MatrixXd& xs, Eigen::MatrixXd& xds) const;
  
  std::ostream& serialize(std::ostream& output) const;
  
  /** 
   * Deserialize (i.e. read) this dynamical system from an input stream.
   * \param[in] input The input stream (which will be modified due to reading from it)
   * \return A pointer to a new dynamical system that was read from the input stream
   */
  static DynamicalSystem* deserialize(std::istream& input);

  /** 
   * Accessor function for damping coefficient.
   * \return Damping coefficient
   */
  inline double damping_coefficient(void) { return damping_coefficient_; }
  
  /** 
   * Accessor function for spring constant.
   * \return Spring constant
   */
  inline double spring_constant(void) { return spring_constant_; }
  
  /** 
   * Accessor function for mass.
   * \return Mass
   */
  inline double mass(void) { return mass_; }
  
private:
  /** Damping coefficient 'c' */
  double damping_coefficient_;

  /** Spring constant 'k' */
  double spring_constant_;

  /** Mass 'm' */
  double mass_;
  

};

#endif // _SPRING_DAMPER_SYSTEM_H_

