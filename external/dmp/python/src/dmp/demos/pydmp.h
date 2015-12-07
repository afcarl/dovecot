
#ifndef _PYDMP_H_
#define _PYDMP_H_

#include <vector>

class PyDMP
{
public:

	/**
     *  Initialization constructor.
     *  \param n_dims 		number of output dimensions. (only 1 is supported)
	 */
	PyDMP(int n_dims);

    ~PyDMP();

	/** Set the algorithmic meta-parameters of the LWR function approximator.
  	 * This is for the special case when the dimensionality of the input data is 1.
 	 *  \param[in] expected_input_dim         The dimensionality of the data this function approximator expects. Since this constructor is for 1-D input data only, we simply check if this argument is equal to 1.
	 *  \param[in] n_basis_functions  Number of basis functions for the one dimension
	 *  \param[in] overlap            Overlap of a basis function with its neighbors
	 *
	 *  The centers and widths of the basis functions are determined from these parameters once the
	 *  range of the input data is known, see also setInputMinMax()
	 */
	void set_lwr_meta_parameters(int expected_input_dim, int n_basis_functions=10, double overlap=0.1);

	/** Set the model parameters of the LWPR function approximator.
     *  \param[in] centers Centers of the basis functions
     *  \param[in] widths  Widths of the basis functions.
     *  \param[in] slopes  Slopes of the line segments.
     *  \param[in] offsets Offsets of the line segments, i.e. the value of the line segment at its intersection with the y-axis.
     */
	void set_lwr_model_parameters(std::vector<double> centers,
								  std::vector<double> widths,
								  std::vector<double> slopes,
								  std::vector<double> offsets);


	void set_initial_state(std::vector<double> init_state);

	void set_attractor_state(std::vector<double> attractor_state);

	/** Set the timesteps at which to compute the states of the dmp.
     *  \param[in] n_timesteps   the number of timesteps.
     *  \param[in] start         when time starts.
     *  \param[in] end           when time ends.
     */
	void set_timesteps(int n_timesteps, double start, double end);

	void generate_trajectory(std::vector<double>& ts,
							 std::vector<double>& ys,
							 std::vector<double>& yds);

private:
	// VSPV: Very Straightforward Private Variables

	int _n_dims;

	bool _meta_set;
	bool _model_set;
	bool _init_set;
	bool _attr_set;
	bool _time_set;

	int _n_basis_functions;
	double _overlap;

	std::vector<double> _centers;
	std::vector<double> _widths;
	std::vector<double> _slopes;
	std::vector<double> _offsets;

	std::vector<double> _init_state;
	std::vector<double> _attractor_state;

	int _n_timesteps;
	double _start;
	double _end;

};

#endif // _PYDMP_H_

