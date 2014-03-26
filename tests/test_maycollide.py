from __future__ import print_function, division, absolute_import
import unittest
import random
import numpy as np

from numpy import cos, sin

import env
from dovecot.collider import maycollide
from dovecot import ttts

class TestMayCollide(unittest.TestCase):

    def test_maycollide(self):
        os_cube = objscene.scenes['cube']
        cf = maycollide.CollisionFilter(os_cube.object_pos, os_cube.object_geoms, 11)

        print(cf.tip((0.0,)*6))

if __name__ == '__main__':
    unittest.main()
