#include "bbo/UpdateSummary.h"

#include "bbo/DistributionGaussian.h"

#include <iostream>
#include <iomanip>
#include <fstream>
#include <boost/filesystem.hpp>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

bool saveToDirectory(const UpdateSummary& summary, string directory, int i_parallel)
{

  // Make directory if it doesn't already exist
  if (!boost::filesystem::exists(directory))
  {
    if (!boost::filesystem::create_directories(directory))
    {
      cerr << __FILE__ << ":" << __LINE__ << ":";
      cerr << "Couldn't make directory file '" << directory << "'." << endl;
      return false;
    }
  }
  
  ofstream file;

  string suffix(".txt");
  if (i_parallel>0)
  {
    stringstream stream;
    stream << setw(2) << setfill('0') << i_parallel << ".txt";
    suffix = stream.str();
  }
  
  // nnn
  DistributionGaussian* distribution_gaussian = dynamic_cast<DistributionGaussian*>(summary.distribution);

  file.open((directory+"distribution_mean"+suffix).c_str());
  file << distribution_gaussian->mean();
  file.close();

  file.open((directory+"distribution_covar"+suffix).c_str());
  file << distribution_gaussian->covar();
  file.close();

  file.open((directory+"cost_eval"+suffix).c_str());
  file << summary.cost_eval;
  file.close();
  
  file.open((directory+"samples"+suffix).c_str());
  file << summary.samples;
  file.close();
  
  file.open((directory+"costs"+suffix).c_str());
  file << summary.costs;
  file.close();
  
  file.open((directory+"weights"+suffix).c_str());
  file << summary.weights;
  file.close();
  
  file.open((directory+"distribution_new_mean"+suffix).c_str());
  file << distribution_gaussian->mean();
  file.close();

  file.open((directory+"distribution_new_covar"+suffix).c_str());
  file << distribution_gaussian->covar();
  file.close();
  
  return true;
  
}


