import forest
import traceback

from dovecot.calibration import tttcal

names={'center_cube',
       'center_cylinder',
       'center_sphere',
       'other_cube',
       'cylinder',
       'calibrate',
      }

tttcal.calibrate(names)