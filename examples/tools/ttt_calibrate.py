import forest
import traceback

import sys

from dovecot.calibration import tttcal

names=['ball0',
       'ball0_wall',
       'smallball0',
       'bigball0',
       'cube0',
       'cube0_wall',
       'cube1',
       'smallcube0',
       'bigcube0',
       'enormouscube0',
       'tube0',
       'calibrate',
       # 'center_cube',
       # 'center_cylinder',
       # 'center_sphere',
       # 'other_cube',
       # 'cylinder',
       # 'center_tinycube',
       # 'center_tinysphere',
       # 'center_tinycylinder',
       # 'side_tinycube',
       # 'side_tinysphere',
       # 'side_tinycylinder',
      ]

if len(sys.argv) == 2:
	name = [sys.argv[1]]
	tttcal.calibrate(name)
else:
	tttcal.calibrate(names)
