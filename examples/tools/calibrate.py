from __future__ import print_function, division
import sys
import time

import env
from surrogates.stemsim import stemcfg
from surrogates.stemsim.calibration import calibr

stem = stemcfg.stems[int(sys.argv[1])]
stem.cycle_usb()

calibr.calibrate(stem, cached_opti=True, cached_vrep=False)
