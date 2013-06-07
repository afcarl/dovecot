import time
import sys

from toolbox import gfx
import pydyn.dynamixel as dyn

import natnet
import tracker


# init pose


class RandomExplore(object):

    def __init__(self, rb_name, ref_point, motors = True, trio = True): # compliant stem
        if motors:
            self.ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6], timeout = 0.05)
        else:
            self.ctrl = None
        if trio:
            self.mt = tracker.MarkerTracker(rb_name, ref_point)
        else:
            self.mt = None

    @property
    def last_pos(self):
        return self.mt._last_pos

    def init_pose(ctrl):

        for m in self.ctrl.motors:
            m.compliant = False
            m.torque = 50
            m.speed = 100
            m.position = 150

        self.ctrl.motors[0].position = 170
        self.ctrl.motors[3].position = 170
        self.ctrl.motors[5].position = 100

        time.sleep(2)

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

    def babble(self):
        order = self.random_order()
        start = time.time()
        for m, o_i in zip(self.ctrl.motors, order):
            m.position = o_i

        collision = False
        lost_track = False
        while time.time() - start < 2.0:
            if not (collision or lost_track):
                pos = get_tip()
                if pos[1] < 0.2:
                    m.speed = True
                    collision = True
                    m.position = m.position
                if pos is None:
                    lost_track = True
            time.sleep(0.001)

        return self._last_pos

if __name__ == "__main__":
    #ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6], timeout = 0.05)
    #init_pose(ctrl)

    rb_name   = 'Rigid Body 1'
    ref_point = (-0.1096, 0.1100,-0.2106) # compliant stem
    #ref_point = (-0.1036, 0.2461, 0.1383) # init pose
    rexpl = RandomExplore(rb_name, ref_point)

    while True:
        rexpl.print_pos()
        time.sleep(0.001)