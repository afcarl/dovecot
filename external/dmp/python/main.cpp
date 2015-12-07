#include <boost/python.hpp>
#include <iostream>

#include "src/dmp/demos/pydmp.h"
#include "GenericList.h"

using namespace boost::python;

class PyDMP_Wrapper{
public:
    PyDMP_Wrapper(int n_dims){
        _pydmp = new PyDMP(n_dims);
    }

    ~PyDMP_Wrapper(){
        delete _pydmp;
    }

    void set_lwr_meta_parameters(int expected_input_dim, int n_basis_functions=10, double overlap=0.1){
        return _pydmp->set_lwr_meta_parameters(expected_input_dim, n_basis_functions, overlap);
    }

    void set_lwr_model_parameters(G_LIST centers, G_LIST widths, G_LIST slopes, G_LIST offsets){
        return _pydmp->set_lwr_model_parameters(castPythonList(centers),
                                                castPythonList(widths),
                                                castPythonList(slopes),
                                                castPythonList(offsets));
    }

    void set_initial_state(G_LIST init_state){
        return _pydmp->set_initial_state(castPythonList(init_state));
    }

    void set_attractor_state(G_LIST attractor_state){
        return _pydmp->set_attractor_state(castPythonList(attractor_state));
    }

    void set_timesteps(int n_timesteps, double start, double end){
        return _pydmp->set_timesteps(n_timesteps, start, end);
    }

    G_LIST generate_trajectory(){
        std::vector<double> * ts = new std::vector<double>();
        std::vector<double> * ys = new std::vector<double>();
        std::vector<double> * yds = new std::vector<double>();
        _pydmp->generate_trajectory(*ts, *ys, *yds);
        GenericList result;
        for(int i = 0 ; i < ts->size() ; i++){
            result.appendDouble(ts->at(i));
            result.appendDouble(ys->at(i));
            result.appendDouble(yds->at(i));
        }
        delete(ts);
        delete(ys);
        delete(yds);
        return result.list();
    }


private:
    PyDMP * _pydmp;

    std::vector<double> castPythonList(G_LIST list){
        std::vector<double> ret;
        GenericList _list = GenericList(list);
        int size_list = _list.size();
        for(int i = 0 ; i < size_list ; i++)
            ret.push_back(_list.readDouble(i));
        return ret;
    }
};

BOOST_PYTHON_MODULE(pydmp)
{
    class_<PyDMP_Wrapper>("PyDMP", init<int>())
        .def("set_lwr_meta_parameters", &PyDMP_Wrapper::set_lwr_meta_parameters)
        .def("set_lwr_model_parameters", &PyDMP_Wrapper::set_lwr_model_parameters)
        .def("set_initial_state", &PyDMP_Wrapper::set_initial_state)
        .def("set_attractor_state", &PyDMP_Wrapper::set_attractor_state)
        .def("set_timesteps", &PyDMP_Wrapper::set_timesteps)
        .def("generate_trajectory", &PyDMP_Wrapper::generate_trajectory)
        ;
}