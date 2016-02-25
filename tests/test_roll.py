from __future__ import print_function, division, absolute_import
import unittest

import numpy as np

import dotdot
from dovecot.ext.dynamics.fwdkin import matrices
from dovecot.prims.s_roll import Roll

class TestRoll(unittest.TestCase):

    def test_roll(self):
        roll = Roll(None)
        roll.process_context(None)


        sensors_data = {'object_ori': []}
        origin_rot = np.matrix([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        for i in range(100):
#            revol_quat = (0.01*i, 0.0, 0.0, math.sqrt(1.0-(0.01*i)**2))
#            revol_rot = matrices.quat2rot(revol_quat)
            revol_rot = np.matrix([[np.cos(0.01*i), -np.sin(0.01*i), 0],
                                   [np.sin(0.01*i),  np.cos(0.01*i), 0],
                                   [             0,               0, 1]])
            quat = matrices.rot2quat(origin_rot*revol_rot)
            sensors_data['object_ori'].append(quat)

        effect = roll.process_sensors(sensors_data)
        self.assertEqual(effect[1], 1.0)
        self.assertTrue(abs(effect[0] - 1.0) < 0.02)

if __name__ == '__main__':
    unittest.main()
