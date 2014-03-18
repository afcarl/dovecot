from __future__ import division, print_function
import sys

from pydyn import MotorSet
import env
from surrogates.stemsim import stemcfg

uid = 0 if len(sys.argv) == 1 else int(sys.argv[1])

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)
for m in ms.motors:
    print(m.ram_desc())