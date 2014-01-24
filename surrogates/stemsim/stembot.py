import time

import numpy as np

from .. import prims
from . import stemcom

class StemBot(object):

    """ This class is responsible of executing the motor primitive only.

        This involves carrying out the movement of the stem, and keeping the motor temp
        low, and solving any hardware problem that may happen.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.m_prim = prims.create_mprim(self.cfg.mprim.name, self.cfg)
        self.stemcom = stemcom.StemCom(cfg)

    @property
    def m_feats(self):
        return self.m_prim.m_feats

    @property
    def m_bounds(self):
        return self.m_prim.m_bounds

    def execute_order(self, order):
        self.stemcom.setup([150.0]*6)

        motor_traj, max_steps = self.m_prim.process_order(order)
        ts = [0.01*i for i in range(len(motor_traj[0][0]))]
        motor_traj = list(zip(*tuple(t_i[0] for t_i in motor_traj)))
        for i, mt_i in enumerate(motor_traj):
            motor_traj[i] = np.degrees(mt_i) + 150.0

        print motor_traj[0]
        print motor_traj[-1]

        self.stemcom.range_bounds = ((140.0, 160.0),) + ((80, 200),)*5
        self.max_speed = 70
        self.max_torque = 40

        start_time = time.time()
        while time.time()-start_time < ts[-1]:
            self.stemcom.step((ts, motor_traj), start_time)

        time.sleep(2.0)

    def close(self):
        self.stemcom.rest()
        self.stemcom.close()