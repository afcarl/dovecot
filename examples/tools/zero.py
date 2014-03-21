from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
from surrogates.stemsim import stemcfg

uid = None if len(sys.argv) == 1 else int(sys.argv[1])

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, timeout=10, verbose=True)
ms.zero_pose = stem.zero_pose

ms.moving_speed = 100
ms.torque_limit = 100
ms.pose = (0.0,)*6

time.sleep(2.0)
print("pos: [{}]".format(', '.join('{:.1f}'.format(p) for p in ms.pose)))
