#include "bbo/DistributionGaussian.h"

#include <fstream>

#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

int main(int n_args, char* args[])
{
  // If program has an argument, it is a directory to which to save files too (or --help)
  string directory;
  if (n_args>1)
    directory = args[1];
    
  int dim = 2;
  VectorXd mean(dim);
  mean << 0.0, 1.0;
  MatrixXd covar(dim,dim);
  covar << 3.0, 0.5, 0.5, 1.0;
  
  DistributionGaussian distribution(mean, covar); 
  DistributionGaussian distribution2(mean, covar); 
  
  // Just to check if they generate different numbers
  int n_samples = 3;
  MatrixXd samples(n_samples,dim);
  distribution.generateSamples(n_samples, samples);
  cout << "________________\nsamples distribution 1 =\n" << samples << endl;
  distribution2.generateSamples(n_samples, samples);
  cout << "________________\nsamples distribution 2 =\n" << samples << endl;

  
  n_samples = 1000;
  distribution.generateSamples(n_samples, samples);
  
  cout << "distribution = " << distribution << endl;

  if (directory.empty())
  {
    cout << "________________\nsamples =\n" << samples << endl;
  } 
  else 
  {
    ofstream outfile;
    string filename = directory+"/samples.txt";
    outfile.open(filename.c_str()); 
    if (!outfile.is_open())
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "Could not open file " << filename << " for writing." << endl;
    } 
    else
    {
      outfile << samples;
      outfile.close();
    }
  }
  
}


