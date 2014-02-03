import time

import numpy as np

from .. import prims
from . import stemcom
from . import collider
from collider import maycollide
from ..vrepsim import objscene

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
        # will check if the movement has a possibility of generating a non-null sensory feedback
        # if not and filter_real_execution is True, it will not be executed.
        self._prefilter = cfg.sprims.prefilter
        if self._prefilter:
            obj_scene = objscene.scenes[self.cfg.sprims.scene]
            self._collision_filter = maycollide.CollisionFilter(obj_scene.object_pos, obj_scene.object_geom, 11)


        self.stemcom = stemcom.StemCom(cfg, **kwargs)

    @property
    def m_feats(self):
        return self.m_prim.m_feats

    @property
    def m_bounds(self):
        return self.m_prim.m_bounds

    def create_trajectory(self, order):
        """ For an order vector, produce a trajectory

            If the order induce a collision with the robot or the static environment, raise CollisionError
        """
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

        return ts, motor_traj

    def execute_order(self, order):
        ts, motor_traj = self.create_trajectory(order)

        if self._prefilter:
            if not self._collision_filter.may_collide(motor_traj):
                return None, None

        self.stemcom.setup(self.cfg.mprim.init_states)
        time.sleep(0.1)

        self.max_speed    = 300
        self.torque_limit = 100

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
