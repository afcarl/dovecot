import time
import sys
import random
import math

from toolbox import gfx
import pydyn.dynamixel as dyn

import natnet
import tracker


# init pose


class RandomExplore(object):

    def __init__(self, ref_point = None, motors = True, trio = True): # compliant stem
        self.ref_point = ref_point

        if motors:
            self.ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6], timeout = 0.05)
        else:
            self.ctrl = None
        if trio:
            assert ref_point is not None
            self.mt = tracker.MarkerTracker(ref_point)
            self.nnclient = self.mt.nnclient
        else:
            self.mt = None

    @property
    def last_pos(self):
        return self.mt._last_pos

    def init_pose(self):

        for m in self.ctrl.motors:
            m.compliant = False
            m.torque = 50
            m.speed = 50
            m.position = 150

        self.ctrl.motors[0].position = 170
        self.ctrl.motors[3].position = 170
        self.ctrl.motors[5].position = 100

        self.sleep(3.0)

    def sleep(self, dur):
        if self.mt is None:
            time.sleep(dur)
        else:
            start = time.time()
            while time.time() - start < dur:
                self.get_tip()
                time.sleep(0.001)

    def random_order(self, span = 30):
        order = []
        for m in self.ctrl.motors:
            order.append(random.uniform(m.position - span, m.position + span))
        return order

    def get_tip(self):
        return self.mt.update()

    def print_pos(self):
        """Print the position with colors"""
        pos = self.mt.update()
        if pos is None:
            color = gfx.red
        else:
            color = gfx.green if pos[1] >= 0.20 else gfx.purple
        print('{}{}{}\r'.format(color, ', '.join('{:+5.4f}'.format(e) for e in self.last_pos), gfx.end)),
        sys.stdout.flush()
        return pos

    def babble(self, span = 30):
        self.init_pose()
        self.mt = tracker.MarkerTracker(self.ref_point, nnclient = self.nnclient)

        pos = self.get_tip()
        d = math.sqrt(sum((a-b)*(a-b) for a, b in zip(pos, self.ref_point)))
        assert d < 0.01, 'distance to reference point is too high (got {}, expected less than {})'.format(d, 0.01)

        order = self.random_order(span = span)

        start = time.time()
        #print order
        for m, o_i in zip(self.ctrl.motors, order):
            m.position = o_i

        collision = False
        lost_track = 0
        while time.time() - start < 2.0:
            if not (collision or lost_track > 5):
                pos = self.print_pos()
                if pos is None:
                    lost_track += 1
                else:
                    lost_track = 0
                    if pos[1] < 0.2:
                        m.speed = True
                        collision = True

                        m.position = m.position

            time.sleep(0.001)
        print

        return self.last_pos

if __name__ == "__main__":
    #ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6], timeout = 0.05)
    #init_pose(ctrl)

    ref_point = (-0.1096, 0.1100,-0.2106) # compliant stem
    ref_point = (-0.1045, 0.2465, 0.1395) # init pose
    rexpl = RandomExplore(ref_point)

    for i in range(100):
        rexpl.babble(span = 60)
    # while True:
    #     rexpl.print_pos()
    #     time.sleep(0.001)