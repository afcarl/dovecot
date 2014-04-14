import forest
import traceback

import sys

from dovecot.calibration import tttcal

names=['center_cube',
       'center_cylinder',
       'center_sphere',
       'other_cube',
       'cylinder',
       'calibrate',
      ]

if len(sys.argv) == 2:
	name = [sys.argv[1]]
	tttcal.calibrate(name)
else:
	tttcal.calibrate(names)
