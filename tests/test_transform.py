from __future__ import print_function, division

import unittest
import random
import numpy as np

from numpy import cos, sin

import env
from surrogates.stemsim.calibration import transform

class TestTransform(unittest.TestCase):

    def test_detect_gaps(self):
        traj = [1, None, None, 2]
        self.assertEqual(transform._detect_gaps(traj), [[1,2]])

    def test_fill_gaps(self):
        traj = [1, None, None, 2]
        self.assertEqual(transform.fill_gaps(traj), [1, 1.0, 1.5, 2])
        traj = [1, 1, 1, 1, 1, 1, None, None, 2]
        self.assertEqual(transform.fill_gaps(traj), [1, 1, 1, 1, 1, 1, 1.0, 1.5, 2])
        traj = [1, None, None, None, None, 2]
        self.assertEqual(transform.fill_gaps(traj), [1, 1.0, 1.25, 1.50, 1.75, 2])

        traj = [(1, 3), None, None, (2, 1)]
        self.assertEqual([tuple(v) for v in transform.fill_gaps(traj)], [(1, 3), ( 1.,  3.), (1.5,  2.), (2, 1)])
