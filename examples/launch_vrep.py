from __future__ import print_function

import forest
import os

import env
from surrogates.vrepsim import vrepbot

cfg = forest.Tree()
cfg._branch('vrep')
cfg.vrep.ppf         = 10

if os.uname()[0] == 'Darwin':
    cfg.vrep.vrep_folder = '/Applications/V-REP/v_rep/bin'
else:
    cfg.vrep.vrep_folder = '/home/fbenurea/external/vrep/3.0.5/'
cfg.vrep.load            = True
cfg.vrep.headless        = False

cfg._branch('sprims')
cfg.sprims.names = ['push']
cfg.sprims.uniformze = False

cfg._branch('mprim')
cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.25

cfg.calib_datas_folder = '~/l2l-files/'

cfg.mprim.init_states   = [-30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [ 30.0, 0.0, 0.0, 0.0, 0.0, 0.0]


if __name__ == "__main__":
    vrepb = vrepbot.VRepBot(cfg)
    vrepb.close()
