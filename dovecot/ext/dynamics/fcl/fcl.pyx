# 3 steps:
#   1. cython fmodel.pyx  -> fmodel.cpp
#   2. link: python setup.py build_ext --inplace  -> fmodel.so, a dynamic library
#   3. python test.py

from libcpp.vector cimport vector

cdef extern from "_fcl.h":
    cdef cppclass PyFCL:
        PyFCL()

        void reset()

        int add_sphere_quat(double radius,
                           double tx, double ty, double tz,
                           double q0, double q1, double q2, double q3)

        int add_box_quat(double x, double y, double z,
                         double tx, double ty, double tz,
                         double q0, double q1, double q2, double q3)

        void collide()

        int collision_count()

        vector[int] get_first_keys();
        vector[int] get_second_keys();


cdef class Fcl:

    cdef PyFCL *thisptr      # hold a C++ instance which we're wrapping

    def __cinit__(self):
        self.thisptr = new PyFCL()

    def __dealloc__(self):
        pass
        #del self.thisptr

    def reset(self):
        self.thisptr.reset()

    def add_shere_quat(self, double radius,
                       double tx, double ty, double tz,
                       double q0, double q1, double q2, double q3):
        cdef double radius_ = radius
        cdef double tx_ = tx
        cdef double ty_ = ty
        cdef double tz_ = tz
        cdef double q0_ = q0
        cdef double q1_ = q1
        cdef double q2_ = q2
        cdef double q3_ = q3
        return self.thisptr.add_sphere_quat(radius_,
                                            tx_, ty_, tz_,
                                            q0_, q1_, q2_, q3_)

    def add_box_quat(self, double x, double y, double z,
                     double tx, double ty, double tz,
                     double q0, double q1, double q2, double q3):
        return self.thisptr.add_box_quat(x, y, z,
                                         tx, ty, tz,
                                         q0, q1, q2, q3)

    def collide(self):
        self.thisptr.collide()

    def collision_count(self):
        return self.thisptr.collision_count()

    def get_first_keys(self):
        keys = self.thisptr.get_first_keys()
        return keys

    def get_second_keys(self):
        keys = self.thisptr.get_second_keys()
        return keys
