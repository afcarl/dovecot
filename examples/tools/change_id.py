from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
from surrogates.stemsim import stemcfg

uid = None if len(sys.argv) == 1 else int(sys.argv[1])

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=(0, 253), verbose=True)

def change(id_change):
    for m in ms.motors:
        if m.id == id_change[0]:
            m.id = id_change[1]
    time.sleep(1.0)

#change((96, 16))