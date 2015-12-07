#include "bbo/updaters/UpdaterMean.h"
#include "bbo/updaters/UpdaterCovarDecay.h"
#include "bbo/updaters/UpdaterCovarAdaptation.h"

#include <eigen3/Eigen/Core>

#include <iomanip> 

using namespace std;
using namespace Eigen;

int main()
{
  
  int n_dims = 2;
  VectorXd mean(n_dims);
  MatrixXd covar = MatrixXd::Zero(n_dims,n_dims);
  for (int ii=0; ii<n_dims; ii++)
  {
    mean(ii) = 1+ii;
    covar(ii,ii) = 0.5*(ii+1);
  }

  // MAKE THE DIFFERENT UPDATERS
  
  Updater* updaters[3];
  
  double eliteness = 10;
  string weighting_method = "PI-BB";
  updaters[0] = new UpdaterMean(eliteness,weighting_method);

  double covar_decay_factor = 0.9;
  updaters[1] = new UpdaterCovarDecay(eliteness,covar_decay_factor,weighting_method);
  
  VectorXd base_level = VectorXd::Constant(n_dims,0.01);
  bool diag_only = true;
  double learning_rate = 1.0;
  updaters[2] = new UpdaterCovarAdaptation(eliteness,weighting_method,base_level,diag_only,learning_rate);  

  DistributionGaussian distribution(mean, covar); 
  int n_samples = 10;
  MatrixXd samples(n_samples,n_dims);
  distribution.generateSamples(n_samples, samples);
  
  // Distance to origin
  VectorXd costs = samples.array().pow(2).rowwise().sum().sqrt();
    
  for (int i_updater=0; i_updater<3; i_updater++)
  {
    cout << "___________________________________________________" << endl;
    
    // Reset to original distribution for each updater
    distribution.set_mean(mean);
    distribution.set_covar(covar);
  
    VectorXd weights;
    UpdaterMean* updater_mean = dynamic_cast<UpdaterMean*>(updaters[i_updater]);
    updater_mean->costsToWeights(costs, weighting_method, eliteness, weights);
    
    cout << setprecision(3);
    cout << setw(10);
    cout << "  samples      = " << samples.transpose() << endl;
    cout << "  costs        = " << costs.transpose()   << endl;
    cout << "  weights      = " << weights.transpose() << endl;
    cout << "  distribution = " << distribution << endl;
    
    updaters[i_updater]->updateDistribution(distribution, samples, costs, distribution);
    cout << "  distribution = " << distribution << endl;
  }
  
}


