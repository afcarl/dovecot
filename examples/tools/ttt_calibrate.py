import scicfg
import traceback

import sys

import dotdot
from dovecot.calibration import tttcal

names=['vanilla',
      ]

if len(sys.argv) == 2:
	name = [sys.argv[1]]
	tttcal.calibrate(name)
else:
	tttcal.calibrate(names)
