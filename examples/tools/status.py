from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
import dovecot
from dovecot.stemsim import stemcfg

if len(sys.argv) >= 2:
    uid = int(sys.argv[1])
else:
    uid = dovecot.stem_uid()

stem = stemcfg.stems[uid]
ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)

print(ms.compliant)
time.sleep(0.1)
