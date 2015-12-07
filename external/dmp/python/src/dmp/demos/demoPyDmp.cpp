#include <iostream>
#include <vector>

#include "pydmp.h"

using namespace std;

int main(int argc, char* argv[])
{
    for (int i=0; i < 100; i++) {

        PyDMP* dmp = new PyDMP(1);

        dmp->set_lwr_meta_parameters(1, 1);
        vector<double> centers = {0.2};
        vector<double> widths  = {1.0};
        vector<double> slopes  = {-100.0};
        vector<double> offsets = {-100.0};
        dmp->set_lwr_model_parameters(centers, widths, slopes, offsets);

        vector<double> init_state  = {1.0};
        dmp->set_initial_state(init_state);
        vector<double> attr_state  = {1.0};
        dmp->set_attractor_state(attr_state);

        dmp->set_timesteps(500, 0.0, 1.0);

        vector<double> ts;
        vector<double> ys;
        vector<double> yds;

        dmp->generate_trajectory(ts, ys, yds);

        delete dmp;

    }
    // for (int i=0; i<ts.size(); i++) {
    // 	cout << ts[i] << '\t' << ys[i] << '\t' << yds[i] << endl;
    // }
    // Eigen::MatrixXd xs_xds_ts(ts.size(), 1+2*n_dims);
    // xs_xds_ts << ys_ana, yds_ana, ts;
    // cout << ys_ana << endl;
    // saveMatrix("/tmp/blabla/", "bla.txt",xs_xds_ts,true);
}