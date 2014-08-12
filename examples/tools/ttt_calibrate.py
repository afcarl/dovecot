import forest
import traceback

import sys

from dovecot.calibration import tttcal

names=['vanilla',
      ]

if len(sys.argv) == 2:
	name = [sys.argv[1]]
	tttcal.calibrate(name)
else:
	tttcal.calibrate(names)
