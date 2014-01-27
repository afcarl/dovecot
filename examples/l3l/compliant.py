import time
import pydyn.dynamixel as dyn

ctrl = dyn.create_controller(verbose = True, motor_range = [0, 50], timeout = 0.05)
for m in ctrl.motors:
    m.compliant = True

time.sleep(0.5)
