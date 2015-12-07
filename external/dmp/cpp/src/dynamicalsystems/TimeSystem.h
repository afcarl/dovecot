/**
 * @file TimeSystem.h
 * @brief  TimeSystem class header file.
 * @author Freek Stulp
 */

#ifndef _TIME_SYSTEM_H_
#define _TIME_SYSTEM_H_

#include "dynamicalsystems/DynamicalSystem.h"

/** \brief Dynamical System modelling the evolution of an Time system: \f$\dot{x} = 1/\tau\f$.
 * 
 * \ingroup DynamicalSystems
 */
class TimeSystem : public DynamicalSystem
{
public:
  
  /**
   *  Initialization constructor.
   *  \param tau              Time constant,                cf. DynamicalSystem::tau()
   *  \param name             Name for the sytem,           cf. DynamicalSystem::name()
   */
  TimeSystem(double tau, std::string name="TimeSystem");
  
  /** Destructor. */
  ~TimeSystem(void);
  
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

};

#endif // _Time_SYSTEM_H_

