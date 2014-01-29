from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
from surrogates.stemsim import stemcfg

stem = stemcfg.stems[int(sys.argv[1])]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)
ms.dyn.io._serial.purge()
time.sleep(1.0)
ms.dyn.io._serial.resetDevice()

time.sleep(1.0)
ms.close()