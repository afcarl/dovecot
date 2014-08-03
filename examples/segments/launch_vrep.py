from __future__ import print_function

import forest
import os

import env
from dovecot.vrepsim import vrepbot

from cfg import cfg0

if os.uname()[0] == 'Darwin':
    cfg0.vrep.vrep_folder = '/Applications/V-REP/v_rep/bin'
else:
    cfg0.vrep.vrep_folder = '/home/fbenurea/external/vrep/3.0.5/'
cfg0.vrep.load            = True
cfg0.vrep.headless        = False

if __name__ == "__main__":
    vrepb = vrepbot.VRepBot(cfg0)
    vrepb.close()
