from __future__ import print_function, division, absolute_import
import unittest
import random

from environments import tools
from dovecot import KinEnvironment
from cfg import cfg0
from dovecot.vrepsim import sim_env


class TestKin(unittest.TestCase):

    def test_kin(self):
        cfg0.execute.kin.force = 50.0
        cfg0.execute.simu.ppf  = 1
        kinenv = KinEnvironment(cfg0)
        cols = []
        n = 1000

        for i in range(n):
            m_signal = tools.random_signal(kinenv.m_channels)
            feedback = kinenv.execute(m_signal)
            collided = feedback['s_signal']['push_saliency'] != 0.0
            if collided:
                cols.append((m_signal, feedback))

        print('{:.2f}% collisions'.format(100*1.0*len(cols)/n))

        vrepb = sim_env.SimulationEnvironment(cfg0)
        for m_signal, feedback in cols:
            print(vrepb.execute(m_signal))


if __name__ == '__main__':
    unittest.main()
