import time
import random

import pydyn.dynamixel as dyn

from vreptracker import VRepTracker


# ctrl.restart()
#
# for m in ctrl.motors:
#     m.position = 140
#
# time.sleep(1)
#
# print vt.pose
#
# time.sleep(1)


class VRepSim(object):

    def __init__(self):
        dyn.enable_vrep()
        self.ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6])
        self.vt = VRepTracker(self.ctrl.io.sim, 'Cube')
        self.vt.start()

        self.mfeats  = tuple(range(-13, 0))
        self.mbounds = ((-150.0, 150.0),)*12 + ((0.0, 300.0),)

        self.sfeats  = tuple(range(3))
        self.sbounds = ((-10.0, 10.0),)*3

    def execute_order(self, order):
        assert len(order) == len(self.mfeats)

        pose0 = order[0:6]
        pose1 = order[6:12]
        maxspeed = order[12]

        self.ctrl.stop_sim()
        time.sleep(1.0)
        self.ctrl.start_sim()
        time.sleep(0.5)
        for p_i, m in zip(pose0, self.ctrl.motors):
            m.speed = maxspeed
            m.position = p_i + 150.0

        time.sleep(1.0)

        for p_i, m in zip(pose1, self.ctrl.motors):
            m.position = p_i + 150.0

        time.sleep(1.0)
        pose = self.vt.pose[0:3]
        return tuple(pose)

if __name__ == "__main__":
    vs = VRepSim()

    while True:
        order = [random.uniform(b_min, b_max) for b_min, b_max in vs.mbounds]
        effect = vs.execute_order(order)
        print ', '.join('{:7.4f}'.format(e_i) for e_i in effect)
        time.sleep(0.2)