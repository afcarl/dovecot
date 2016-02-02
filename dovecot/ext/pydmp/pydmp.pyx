# 3 steps:
#   1. cython fmodel.pyx  -> fmodel.cpp
#   2. link: python setup.py build_ext --inplace  -> fmodel.so, a dynamic library
#   3. python test.py

from libcpp.vector cimport vector

cdef extern from "_dmp.h":
    cdef cppclass PyDMP:
        PyDMP(int n_dims)

        void set_lwr_meta_parameters(int expected_input_dim,
                                     int n_basis_functions,
                                     double overlap)

        void set_lwr_model_parameters(vector[double] centers,
                                      vector[double] widths,
                                      vector[double] slopes,
                                      vector[double] offsets)

        void set_initial_state(vector[double] init_state)

        void set_attractor_state(vector[double] attractor_state)

        void set_timesteps(int n_timesteps, double start, double end)

        void generate_trajectory(vector[double] ts,
                                 vector[double] ys,
                                 vector[double] yds)

cdef class DMP:

    cdef PyDMP *thisptr      # hold a C++ instance which we're wrapping

    def __cinit__(self, int n_dims):
        self.thisptr = new PyDMP(n_dims)

    def __dealloc__(self):
        pass
        #del self.thisptr

    def set_lwr_meta_parameters(self,
                                int expected_input_dim,
                                int n_basis_functions,
                                double overlap):
        self.thisptr.set_lwr_meta_parameters(expected_input_dim,
                                             n_basis_functions,
                                             overlap)

    def set_lwr_model_parameters(self,
                                 vector[double] centers,
                                 vector[double] widths,
                                 vector[double] slopes,
                                 vector[double] offsets):
        self.thisptr.set_lwr_model_parameters(centers, widths, slopes, offsets)

    def set_initial_state(self, vector[double] init_state):
        self.thisptr.set_initial_state(init_state)

    def set_attractor_state(self, vector[double] attractor_state):
        self.thisptr.set_attractor_state(attractor_state)

    def set_timesteps(self, int n_timesteps, double start, double end):
        self.thisptr.set_timesteps(n_timesteps, start, end)

    def generate_trajectory(self):
        cdef vector[double] ts  = []
        cdef vector[double] ys  = []
        cdef vector[double] yds = []
        self.thisptr.generate_trajectory(ts, ys, yds)
        return ts, ys, yds
