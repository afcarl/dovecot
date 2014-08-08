from __future__ import print_function, division, absolute_import
import unittest
import random

from environments import tools
from dovecot import KinEnvironment
from cfg import cfg0




class TestKin(unittest.TestCase):

    def test_kin(self):
        cfg0.execute.kin.force = 50.0
        kinenv = KinEnvironment(cfg0)
        c = 0
        n = 1000

        for i in range(n):
            m_signal = tools.random_signal(kinenv.m_channels)
            feedback = kinenv.execute(m_signal)
            collided = feedback['s_signal']['push_saliency'] != 0.0
            if collided:
                c += 1

        print('{:.2f}% collisions'.format(100*1.0*c/n))

if __name__ == '__main__':
    unittest.main()
