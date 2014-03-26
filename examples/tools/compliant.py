from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
from dovecot.stemsim import stemcfg

uid = None if len(sys.argv) == 1 else int(sys.argv[1])

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)

for m in ms.motors:
    m.status_return_level = 1
    time.sleep(0.1)
ms.compliant = True
time.sleep(0.1)
