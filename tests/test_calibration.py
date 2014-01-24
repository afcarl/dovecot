from __future__ import print_function, division

import unittest
import random
import numpy as np

from numpy import cos, sin

import env
from surrogates.stemsim import opti_calibr

class TestCalibration(unittest.TestCase):

    def test_transform3D(self):

        def RotX(theta):
            return np.matrix([[1,          0,           0],
                              [0, cos(theta), -sin(theta)],
                              [0, sin(theta),  cos(theta)]])

        def RotY(theta):
            return np.matrix([[ cos(theta), 0, sin(theta)],
                              [          0, 1,          0],
                              [-sin(theta), 0, cos(theta)]])

        def RotZ(theta):
            return np.matrix([[cos(theta), -sin(theta), 0],
                              [sin(theta),  cos(theta), 0],
                              [         0,           0, 1]])


        for _ in range(100):

            Rx = RotX(random.uniform(-np.pi, np.pi))
            Ry = RotY(random.uniform(-np.pi, np.pi))
            Rz = RotZ(random.uniform(-np.pi, np.pi))

            R = Rx*Ry*Rz
            T = np.mat(np.random.rand(3,1))
            s = random.uniform(0.0, 10.0)

            n = 10

            A = np.mat(np.random.rand(5,3))
            B = R*s*A.T + np.tile(T, (1, 5))
            B = B.T

            # homogeneous matrices
            Ah = np.hstack([A, np.ones(shape=(A.shape[0], 1))])
            Bh = np.hstack([B, np.ones(shape=(A.shape[0], 1))])

            Mtrans = opti_calibr.transform_3D(A, B)

            Ch = (Mtrans*Ah.T).T

            err = Ch - Bh
            err = np.sum(np.multiply(err, err))
            rmse = np.sqrt(err/A.shape[0])

            self.assertTrue(rmse < 1e-10)
