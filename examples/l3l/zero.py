from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
from surrogates.stemsim import stemcfg

uid = None if len(sys.argv) == 1 else int(sys.argv[1])

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)
ms.zero_pose = stem.zero_pose

ms.compliant = False
time.sleep(1.0)
while not all(m.torque_limit==100 for m in ms.motors):
    for m in ms.motors:
        m.max_torque = 100
        m.torque_limit = 100
    time.sleep(1.0)

ms.moving_speed  = 100
m.torque = 100
ms.pose = (0.0,)*6

time.sleep(3.0)
print("pos: [{}]".format(', '.join('{:.1f}'.format(p) for p in ms.pose)))