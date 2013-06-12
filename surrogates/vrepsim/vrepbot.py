import time
import random
import math

import treedict

from toolbox import gfx
import pydyn.dynamixel as dyn

from vreptracker import VRepTracker


defaultcfg = treedict.TreeDict()

defaultcfg.objectname = 'cube'
defaultcfg.objectname_desc = 'Name of object to be tracked in the simulation'

obj_init = (+0.0045, +0.0820, +1.4798)

def distance(a, b):
    return math.sqrt(sum((a_i-b_i)*(a_i-b_i) for a_i, b_i in zip(a, b)))


class VRepSim(object):

    def __init__(self, cfg, **kwargs):
        dyn.enable_vrep()

        self.cfg = cfg
        self.cfg.update(defaultcfg, overwrite = False)

        self.ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6])
        self.vt = VRepTracker(self.ctrl.io.sim, self.cfg.objectname)
        self.vt.start()

        self.m_feats  = tuple(range(-13, 0))
        self.m_bounds = ((-100.0, 100.0),)*5 + ((-60.0, 60.0),)
        self.m_bounds = self.m_bounds*2 + ((0.0, 300.0),)

        self.s_feats  = tuple(range(4))
        self.s_bounds = ((-3.0, 3.0), (-3.0, 3.0), (1.4, 1.6), (0.0, 1.0))

    @property
    def _arm_pos(self):
        return (m.position-150.0 for m in self.ctrl.motors)

    def wait(self, target_pose, dur):
        start = time.time()
        stability = 0
        last_pose = target_pose
        while time.time() - start < dur-0.1:
            pose = self._arm_pos
            if all(abs(ap_i - p_i) < 0.5 for ap_i, p_i in zip(pose, target_pose)):
                time.sleep(0.05)
                return True
            # else:
            #     if all(abs(p1_i - p2_i) < 0.001 and p1_i != p2_i for ap_i, p_i in zip(pose, last_pose)):
            #         stability += 1
            #     else:
            #         stability = 0
            #         last_pose = pose
            # if stability > 5:
            #     return False
            time.sleep(0.01)

        time.sleep(0.05)
        return False

    def execute_order(self, order, **kwargs):
        assert len(order) == len(self.m_feats)

        pose0 = order[0:6]
        pose1 = order[6:12]
        maxspeed = order[12]

        self.ctrl.stop_sim()
        time.sleep(0.1)

        self.ctrl.start_sim()
        time.sleep(0.1)
        assert all(abs(ap_i) < 1.0 for ap_i in self._arm_pos)

        pose = self.vt.pose[0:3] # crucial ! refresh the registering
        for p_i, m in zip(pose0, self.ctrl.motors):
            m.speed = maxspeed
            m.position = p_i + 150.0

        self.wait(pose0, 0.5)

        for p_i, m in zip(pose1, self.ctrl.motors):
            m.position = p_i + 150.0

        self.wait(pose1, 0.5)
        #print max(abs(m.position-p_i-150.0) for m, p_i in zip(self.ctrl.motors, pose1))
        pose = self.vt.pose[0:3]

        if distance(obj_init, pose) > 0.1:
            return tuple(pose) + (1.0,)
        else:
            return tuple(pose) + (0.0,)

