from __future__ import division, print_function
import sys
import time

from dovecot.ext.pydyn import MotorSet
import dotdot
import dovecot
from dovecot.stemsim import stemcfg

if len(sys.argv) >= 2:
    uid = int(sys.argv[1])
else:
    uid = dovecot.stem_uid()

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)
for m in ms.motors:
    print(m.eeprom_desc())
