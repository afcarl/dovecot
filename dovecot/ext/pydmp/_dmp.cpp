#include <iostream>
#include <eigen3/Eigen/Core>

#include <functionapproximators/FunctionApproximatorLWR.hpp>
#include <functionapproximators/MetaParametersLWR.hpp>
#include <functionapproximators/ModelParametersLWR.hpp>

#include <dmp/Dmp.hpp>

#include "_dmp.h"

using namespace std;
using namespace DmpBbo;

PyDMP::PyDMP(int n_dims) {
	assert(n_dims == 1);
	_n_dims = n_dims;

	_meta_set  = false;
	_model_set = false;
	_init_set  = false;
	_attr_set  = false;
	_time_set  = false;
}

void PyDMP::generate_trajectory(std::vector<double>& ts,
						        std::vector<double>& ys,
						        std::vector<double>& yds) {
	assert(_meta_set && _model_set && _init_set && _attr_set && _time_set);

    // Make function approximators
    vector<FunctionApproximator*> function_approximators(_n_dims);
  	MetaParametersLWR* meta_parameters = new MetaParametersLWR(_n_dims, _n_basis_functions, _overlap);
  	for (int dd=0; dd<_n_dims; dd++) {

  		Eigen::Map<Eigen::VectorXd> centers(&_centers[0], _n_basis_functions);
		Eigen::Map<Eigen::VectorXd> widths(&_widths[0],  _n_basis_functions);
		Eigen::Map<Eigen::VectorXd> slopes(&_slopes[0],  _n_basis_functions);
		Eigen::Map<Eigen::VectorXd> offsets(&_offsets[0], _n_basis_functions);

  		ModelParametersLWR* model_parameters = new ModelParametersLWR(centers, widths, slopes, offsets);
   	 	function_approximators[dd] = new FunctionApproximatorLWR(meta_parameters, model_parameters);
        delete model_parameters;
  	}
    delete meta_parameters;

	// Initialize DMP
	Dmp::DmpType dmp_type = Dmp::KULVICIUS_2012_JOINING;
	Dmp* dmp = new Dmp(_n_dims, function_approximators, dmp_type);
    for (int i =0; i < _n_dims; i++) {
        delete function_approximators[i];
    }

	Eigen::VectorXd y_init = Eigen::VectorXd::Map(&_init_state[0], _n_dims);
	dmp->set_initial_state(y_init);
	Eigen::VectorXd y_attr = Eigen::VectorXd::Map(&_attractor_state[0], _n_dims);
	dmp->set_attractor_state(y_attr);

  	// Compute trajectory
	Eigen::VectorXd _ts = Eigen::VectorXd::LinSpaced(_n_timesteps, _start, _end);

	// TODO: replace by void analyticalSolution(const Eigen::VectorXd& ts, Trajectory& trajectory) const
    Eigen::MatrixXd _xs, _xds, _forcing_terms;
    dmp->analyticalSolution(_ts, _xs, _xds, _forcing_terms);
    Eigen::MatrixXd _ys, _yds, _ydds;
    dmp->statesAsTrajectory(_xs, _xds, _ys, _yds, _ydds);

    delete dmp;

    assert(_n_dims == 1);

    ts.clear();
    ys.clear();
    yds.clear();
    for(int i = 0; i < _n_timesteps; i++) {
    	ts.push_back(_ts(i));
		ys.push_back(_ys(i, 0));
		yds.push_back(_yds(i, 0));
	}


}

PyDMP::~PyDMP(){}

void PyDMP::set_lwr_meta_parameters(int expected_input_dim, int n_basis_functions, double overlap) {
	assert(expected_input_dim == _n_dims);

	if (_model_set) {
		assert(_centers.size() == n_basis_functions);
	}

	_n_basis_functions = n_basis_functions;
	_overlap = overlap;

	_meta_set = true;
}

void PyDMP::set_lwr_model_parameters(std::vector<double> centers,
							  		 std::vector<double> widths,
							  		 std::vector<double> slopes,
							  		 std::vector<double> offsets) {


	int n;
	if (_meta_set) { n = _n_basis_functions; } else { n = centers.size(); }

	assert(centers.size() == n);
	assert(widths.size()  == n);
	assert(slopes.size()  == n);
	assert(offsets.size() == n);

	_centers = centers;
	_widths  = widths;
	_slopes  = slopes;
	_offsets = offsets;

	_model_set = true;
}

void PyDMP::set_initial_state(std::vector<double> init_state) {
	assert(init_state.size() == _n_dims);

	_init_state = init_state;
	_init_set = true;
}

void PyDMP::set_attractor_state(std::vector<double> attractor_state) {
	assert(attractor_state.size() == _n_dims);

	_attractor_state = attractor_state;
	_attr_set = true;
}

void PyDMP::set_timesteps(int n_timesteps, double start, double end) {
	assert (n_timesteps >= 0);
	assert (end >= start);
	_n_timesteps = n_timesteps;
	_start = start;
	_end = end;

	_time_set = true;
}
