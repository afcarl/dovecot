import time
import sys

from toolbox import gfx
import pydyn.dynamixel as dyn

import natnet
import tracker

ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6], timeout = 0.05)

# init pose
def init_pose():

    for m in ctrl.motors:
        m.compliant = False
        m.torque = 50
        m.speed = 100
        m.position = 150

    ctrl.motors[0].position = 170
    ctrl.motors[3].position = 170
    ctrl.motors[5].position = 100

    time.sleep(2)


if __name__ == "__main__":
    init_pose()

    rb_name   = 'Rigid Body 1'
    ref_point = (-0.1096, 0.1100,-0.2106) # compliant stem
    ref_point = (-0.1036, 0.2461, 0.1383) # init pose
    mt = tracker.MarkerTracker(rb_name, ref_point)

    last_pos = ref_point
    while True:
        pos = mt.update()
        if pos is None:
            color = gfx.red
        else:
            last_pos = pos
            color = gfx.green
        print('{}{}{}\r'.format(color, ', '.join('{:+5.4f}'.format(e) for e in last_pos), gfx.end)),
        sys.stdout.flush()
        time.sleep(0.01)