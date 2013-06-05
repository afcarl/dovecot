import time

import pydyn.dynamixel as dyn
import natnet

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

    time.sleep(2)

init_pose()
