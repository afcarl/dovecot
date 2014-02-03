import time

import numpy as np

from .. import prims
from . import stemcom
from . import collider

class CollisionError(Exception):
    pass

class StemBot(object):

    """ This class is responsible of executing the motor primitive only.

        This involves carrying out the movement of the stem, and keeping the motor temp
        low, and solving any hardware problem that may happen.
    """

    def __init__(self, cfg, **kwargs):
        self.cfg = cfg
        self.m_prim = prims.create_mprim(self.cfg.mprim.name, self.cfg)
        self.stemcom = stemcom.StemCom(cfg, **kwargs)

    @property
    def m_feats(self):
        return self.m_prim.m_feats

    @property
    def m_bounds(self):
        return self.m_prim.m_bounds

    def create_trajectory(self, order):
        motor_traj, max_steps = self.m_prim.process_order(order)

        ts = [0.01*i for i in range(len(motor_traj[0][0]))]

        motor_traj = list(zip(*tuple(t_i[0] for t_i in motor_traj)))
        for i, mt_i in enumerate(motor_traj):
            motor_traj[i] = np.degrees(mt_i)

        # check for collisions beforehand
        for i, pose in enumerate(motor_traj):
            if len(collider.collide(pose)) > 0:
                raise CollisionError
            #print('{}/{}'.format(i+1, len(pose)), end'\r')
            #sys.stdout.flush()

        # print motor_traj[0]
        # print motor_traj[-1]

        return ts, motor_traj

    def execute_order(self, order):
        ts, motor_traj = self.create_trajectory(order)

        self.stemcom.setup(self.cfg.mprim.init_states)
        time.sleep(0.1)

        self.max_speed    = 100
        self.torque_limit = 70

        start_time = time.time()
        while time.time()-start_time < ts[-1]:
            self.stemcom.step((ts, motor_traj), start_time)
        end_time = time.time()

        time.sleep(0.05)
        self.stemcom.setup(self.cfg.mprim.init_states, blocking=False)

        return start_time, end_time

    def close(self, rest=True):
        if rest:
            self.stemcom.rest()
        self.stemcom.close()
