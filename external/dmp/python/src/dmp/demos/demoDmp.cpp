#include <string>
#include <set>
#include <fstream>
#include <iostream>
#include <eigen3/Eigen/Core>

#include "functionapproximators/FunctionApproximatorLWR.hpp"
#include "functionapproximators/MetaParametersLWR.hpp"
#include "functionapproximators/ModelParametersLWR.hpp"

//#include "utilities/EigenFileIO.hpp"

#include "dmp/Dmp.h"

using namespace std;

int main(int argc, char* argv[])
{

    int n_dims = 1;
    int n_basis_functions = 1;

    // Make function approximators
    vector<FunctionApproximator*> function_approximators(n_dims);
  	MetaParametersLWR* meta_parameters = new MetaParametersLWR(1, 1);
  	for (int dd=0; dd<n_dims; dd++) {

		Eigen::VectorXd centers = Eigen::VectorXd::Constant(n_basis_functions, 0.2);
	  	Eigen::VectorXd widths  = Eigen::VectorXd::Constant(n_basis_functions, 1.0);
	  	Eigen::VectorXd slopes  = Eigen::VectorXd::Constant(n_basis_functions, -100.0);
	  	Eigen::VectorXd offsets = Eigen::VectorXd::Constant(n_basis_functions, -100.0);

  		ModelParametersLWR* model_parameters = new ModelParametersLWR(centers, widths, slopes, offsets);
   	 	function_approximators[dd] = new FunctionApproximatorLWR(meta_parameters, model_parameters);
  	}

	// Initialize and train DMP
	Dmp::DmpType dmp_type = Dmp::KULVICIUS_2012_JOINING;
	Dmp* dmp = new Dmp(n_dims, function_approximators, dmp_type);

	Eigen::VectorXd y_init = Eigen::VectorXd::Constant(n_dims, 0.0);
	dmp->set_initial_state(y_init);
	Eigen::VectorXd y_attr = Eigen::VectorXd::Constant(n_dims, 1.0);
	dmp->set_attractor_state(y_attr);

	Eigen::VectorXd ts = Eigen::VectorXd::LinSpaced(60,0.0,1.0);

    Eigen::MatrixXd xs_ana, xds_ana, forcing_terms;
    dmp->analyticalSolution(ts,xs_ana,xds_ana,forcing_terms);
    Eigen::MatrixXd ys_ana, yds_ana, ydds_ana;
    dmp->statesAsTrajectory(xs_ana,xds_ana,ys_ana,yds_ana,ydds_ana);

	printf("bla2\n");

    Eigen::MatrixXd xs_xds_ts(ts.size(), 1+2*n_dims);
    xs_xds_ts << ys_ana, yds_ana, ts;
    cout << ys_ana << endl;
    saveMatrix("/tmp/blabla/", "bla.txt",xs_xds_ts,true);
}