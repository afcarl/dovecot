from __future__ import print_function, division
import sys
import time

import env
from dovecot.stemsim import stemcfg
from dovecot.calibration import triocal

stem = stemcfg.stems[int(sys.argv[1])]
stem.cycle_usb()

triocal.calibrate(stem, cached_opti=False, cached_vrep=False)
