from __future__ import division, print_function, absolute_import
import time

import numpy as np

import powerswitch as ps
import pydyn

from .. import ttts
from .. import prims
from ..collider import maycollide
from ..collider import collider
from . import stemcfg
from . import stemcom

class CollisionError(Exception):
    pass

TORQUE_LIMIT = 50

class StemBot(object):

    """ This class is responsible of executing the motor primitive only.

        This involves carrying out the movement of the stem, and keeping the motor temp
        low, and solving any hardware problem that may happen.
    """

    def __init__(self, cfg, **kwargs):
        self.cfg = cfg
        # will check if the movement has a possibility of generating a non-null sensory feedback
        # if not and filter_real_execution is True, it will not be executed.
        self._prefilter = cfg.sprims.prefilter
        if self._prefilter:
            caldata = ttts.TTTCalibrationData('ar_'+cfg.sprims.scene, cfg.vrep.calibrdir)
            caldata.load()
            self._collision_filter = maycollide.CollisionFilter(caldata.position, caldata.dimensions, 11)

        self.powerswitch = ps.Eps4m(stemcfg.stems[cfg.stem.uid].powerswitch_mac)
        self.powerswitch_port = stemcfg.stems[cfg.stem.uid].powerswitch
        if self.powerswitch.is_off(self.powerswitch_port):
            self.powerswitch.set_on(self.powerswitch_port)
            time.sleep(1)
        while self.powerswitch.is_restarting(self.powerswitch_port):
            time.sleep(1)

        self.stemcom = stemcom.StemCom(cfg, **kwargs)
        if 'angle_ranges' not in self.cfg.mprim:
            self.cfg.mprim.angle_ranges = self.stemcom.ms.angle_ranges
        self.m_prim = prims.create_mprim(self.cfg.mprim.name, self.cfg)
        self.m_prim.process_context({})
        self.partial_mvt = self.cfg.partial_mvt # when doing test, we do the tests even if they generate collisions:
                                          # we stop just before the collision

    @property
    def m_feats(self):
        return self.m_prim.m_feats

    @property
    def m_bounds(self):
        return self.m_prim.m_bounds

    def create_trajectory(self, order, partial_mvt=False):
        """ For an order vector, produce a trajectory

            If the order induce a collision with the robot or the static environment,
                if partial, return the non-collision prefix
                else raise CollisionError
        """
        motor_traj, max_steps = self.m_prim.process_order(order)

        ts = [0.01*i for i in range(len(motor_traj[0][0]))]

        motor_traj = list(zip(*tuple(t_i[0] for t_i in motor_traj)))
        for i, mt_i in enumerate(motor_traj):
            motor_traj[i] = np.degrees(mt_i)

        # check for collisions beforehand
        for i, pose in enumerate(motor_traj):
            if i % 5 == 0: # every 50ms.
                if len(collider.collide(pose)) > 0:
                    if partial_mvt:
                        return ts[:i-10], motor_traj[:i-10]

                    raise CollisionError
            #print('{}/{}'.format(i+1, len(pose)), end'\r')
            #sys.stdout.flush()

        return ts, motor_traj

    def execute_order(self, order):

        ts, motor_traj = self.create_trajectory(order, partial_mvt=self.partial_mvt)

        if self._prefilter:
            if not self._collision_filter.may_collide(motor_traj):
                return None, None


        try:
            self.stemcom.setup(self.cfg.mprim.init_states)
            time.sleep(0.1)

            self.stemcom.ms.torque_limit = TORQUE_LIMIT

            start_time = time.time()
            while time.time()-start_time < ts[-1]:
                self.stemcom.step((ts, motor_traj), start_time)
            end_time = time.time()

            self.stemcom.setup(self.cfg.mprim.init_states, blocking=False)

            return start_time, end_time
        except pydyn.MotorError as e:
            print("MotorError")
            self.powerswitch.set_off(self.powerswitch_port)
            import traceback
            traceback.print_exc()
            raise e


    def close(self, rest=True):
        if rest:
            self.stemcom.rest()
        self.stemcom.close()
