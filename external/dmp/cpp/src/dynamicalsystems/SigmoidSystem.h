/**
 * @file SigmoidSystem.h
 * @brief  SigmoidSystem class header file.
 * @author Freek Stulp
 */

#ifndef _SIGMOID_SYSTEM_H_
#define _SIGMOID_SYSTEM_H_

#include "dynamicalsystems/DynamicalSystem.h"

/** \brief Dynamical System modelling the evolution of a sigmoidal system \f$\dot{x} = -\alpha x(1-x/K)\f$.
 *
 * \ingroup DynamicalSystems
 */
class SigmoidSystem : public DynamicalSystem
{
public:

  /**
   *  Initialization constructor for a 1D system.
   *  \param tau              Time constant,                cf. DynamicalSystem::tau()
   *  \param x_init           Initial state,                cf. DynamicalSystem::initial_state()
   *  \param max_rate         Maximum rate of change,       cf. SigmoidSystem::max_rate()
   *  \param inflection_point_time Time at which maximum rate of change is achieved,  cf. SigmoidSystem::inflection_point_time()
   *  \param name             Name for the sytem,           cf. DynamicalSystem::name()
   */
   SigmoidSystem(double tau, const Eigen::VectorXd& x_init, double max_rate, double inflection_point_time, std::string name="SigmoidSystem");
  
  /** Destructor. */
  ~SigmoidSystem(void);

  DynamicalSystem* clone(void) const;

  void differentialEquation(const Eigen::VectorXd& x, Eigen::Ref<Eigen::VectorXd> xd) const;
 
  void analyticalSolution(const Eigen::VectorXd& ts, Eigen::MatrixXd& xs, Eigen::MatrixXd& xds) const;

  void set_tau(double tau);
  void set_initial_state(const Eigen::VectorXd& y_init);

  std::ostream& serialize(std::ostream& output) const;
  
  /** 
   * Deserialize (i.e. read) a DynamicalSystem from an input stream.
   * \param[in] input The input stream (which will be modified due to reading from it)
   * \return A pointer to a new object that was read from the input stream
   */
  static DynamicalSystem* deserialize(std::istream& input);

private:
  static Eigen::VectorXd computeKs(const Eigen::VectorXd& N_0s, double r, double inflection_point_time_time);
  
  double max_rate_;
  double inflection_point_time_;
  Eigen::VectorXd Ks_;
  
};

#endif // _Sigmoid_SYSTEM_H_

