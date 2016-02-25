from __future__ import print_function, division, absolute_import
import unittest

import dotdot
from dovecot.stemsim import triopost


def ts(pos):
    return [(i, t_i) for i, t_i in enumerate(pos)]


class TestTransform(unittest.TestCase):

    def test_detect_gaps(self):
        traj = [34, None, None, 21]
        self.assertEqual(triopost._detect_gaps(ts(traj)), [[1,2]])

    def test_fill_gaps(self):
        traj = [1, None, None, 2]
        self.assertEqual(triopost.fill_gaps(ts(traj)), ts([1, 1.0, 1.5, 2]))
        # traj = [[i, t_i] for i, t_i in enumerate([1, 1, 1, 1, 1, 1, None, None, 2])]
        # self.assertEqual(triopost.fill_gaps(traj), [1, 1, 1, 1, 1, 1, 1.0, 1.5, 2])
        # traj = [[i, t_i] for i, t_i in enumerate([1, None, None, None, None, 2])]
        # self.assertEqual(triopost.fill_gaps(traj), [1, 1.0, 1.25, 1.50, 1.75, 2])

        # traj = [[i, t_i] for i, t_i in enumerate([(1, 3), None, None, (2, 1)])]
        # self.assertEqual([tuple(v) for v in triopost.fill_gaps(traj)], [(1, 3), ( 1.,  3.), (1.5,  2.), (2, 1)])

if __name__ == '__main__':
    unittest.main()
