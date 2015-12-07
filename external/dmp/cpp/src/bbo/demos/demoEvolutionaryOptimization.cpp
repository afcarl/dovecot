/**
 * \file demoEvolutionaryOptimization.cpp
 * \author Freek Stulp
 * \brief  Demonstrates how to run an evolution strategy to optimize a distance function, implemented as a CostFunction.
 *
 * \ingroup Demos
 * \ingroup BBO
 */

#include "bbo/CostFunction.h"
#include "bbo/runEvolutionaryOptimization.h"
#include "bbo/DistributionGaussian.h"

#include "bbo/updaters/UpdaterMean.h"
#include "bbo/updaters/UpdaterCovarDecay.h"
#include "bbo/updaters/UpdaterCovarAdaptation.h"

#include <iomanip> 
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;


/** CostFunction in which the distance to a pre-defined point must be minimized.
 *
 * \ingroup BBO
 * \ingroup Demos
 */
class CostFunctionDistanceToPoint : public CostFunction
{
public:
  /** Constructor.
   * \param[in] point Point to which distance must be minimized.
   */
  CostFunctionDistanceToPoint(const VectorXd& point)
  {
    point_ = point;
  }
  
  /** The cost function which defines the cost_function.
   *
   * \param[in] samples The samples 
   * \param[in] cost_function_parameters Optional parameters of the cost_function, and thus the cost function.
   * \param[out] costs The scalar cost for each sample.
   */
  void evaluate(const MatrixXd& samples, const MatrixXd& cost_function_parameters, VectorXd& costs) const {
    // cost_vars       = n_samples x n_dim
    // cost_function_parameters = n_samples x n_cost_function_parameters
    // costs           = n_samples x 1
  
    // Cost is distance to point
    int n_samples = samples.rows();
    costs.resize(n_samples);
    for (int ss=0; ss<n_samples; ss++)
    {
      costs[ss] = sqrt((samples.row(ss) - point_.transpose()).array().pow(2).sum());
    }
  }
  
  /** Write object to output stream. 
   *  \param[in] output Output stream to which to write to 
   *  \return Output stream to which the object was written 
   */
  ostream& serialize(ostream& output) const {
    output << "CostFunctionDistanceToPoint[point=" << point_.transpose() << "]";
    return output;
  }

private:
  /** Point to which distance is computed. */
  VectorXd point_;
  
};

/** Main function
 * \param[in] n_args Number of arguments
 * \param[in] args Arguments themselves
 * \return Success of exection. 0 if successful.
 */
int main(int n_args, char* args[])
{
  // If program has an argument, it is a directory to which to save files too (or --help)
  string directory;
  if (n_args>1)
  {
    if (string(args[1]).compare("--help")==0)
    {
      cout << "Usage: " << args[0] << " [directory]         (directory: optional directory to save data to)" << endl;
      return 0;
    }
    else
    {
      directory = string(args[1]);
    }
  }
  
  int n_dims = 2;
  //VectorXd minimum = VectorXd::LinSpaced(n_dims,1,n_dims);
  VectorXd minimum = VectorXd::Zero(n_dims);
  
  CostFunction* cost_function = new CostFunctionDistanceToPoint(minimum);
  
  VectorXd mean_init  =  5.0*VectorXd::Ones(n_dims);
  MatrixXd covar_init =  4.0*MatrixXd::Identity(n_dims,n_dims);
  DistributionGaussian* distribution = new DistributionGaussian(mean_init, covar_init); 
  
  Updater* updater = NULL;
  double eliteness = 10;
  string weighting_method = "PI-BB";
    
  if (false)
  {
    updater = new UpdaterMean(eliteness,weighting_method);
  }
  
  if (false)
  {
    double covar_decay_factor = 0.8;
    updater = new UpdaterCovarDecay(eliteness,covar_decay_factor,weighting_method);
  }
  
  if (updater==NULL)
  {
    VectorXd base_level = VectorXd::Constant(n_dims,0.000001);
    eliteness = 10;
    bool diag_only = false;
    double learning_rate = 0.5;
    updater = new UpdaterCovarAdaptation(eliteness,weighting_method,base_level,diag_only,learning_rate);  
  }
    
  
  int n_samples_per_update = 10;
  
  int n_updates = 20;
  
  runEvolutionaryOptimization(cost_function, distribution, updater, n_updates, n_samples_per_update,directory);
  
}


