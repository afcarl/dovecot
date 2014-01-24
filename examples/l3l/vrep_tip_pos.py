from __future__ import division, print_function
import time
import random
import os
import numpy as np

import treedict

import env
from surrogates.vrepsim import vrepbot
from surrogates import prims

cfg = treedict.TreeDict()
cfg.vrep.ppf         = 10

if os.uname()[0] == 'Darwin':
    cfg.vrep.vrep_folder = '/Applications/V-REP/v_rep/bin'
else:
    cfg.vrep.vrep_folder = '/home/fbenurea/external/vrep/3.0.5/'
cfg.vrep.load            = True
cfg.vrep.headless        = False

cfg.sprims.names = ['push']
cfg.sprims.uniformze = False

cfg.sensors.tip = True

cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 1000
cfg.mprim.max_steps   = 1000
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 2.0

cfg.mprim.init_states   = [-30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [  0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

target_states = [[  0.0,   0.0,   0.0,   0.0,   0.0,   0.0],
                 [ 57.2,  11.6, -10.7,  14.1,   6.0, -17.7],
                 [ -4.1,  -9.8,   9.8, -34.9,   5.7, -19.2],
                 [ -4.4,  -0.4,  -5.7,  -2.6, -69.1, -17.7],
                 [ -4.1,   5.1,  -8.9,   2.4,  80.8,  13.6],
                 [44.3,  -99.0,  33.6, -15.2,  72.3, -25.1],
                 [-3.8,   43.5,  25.7,  -3.8,  72.3, -42.7],
                 [-25.8, -99.0,  45.6,  -7.9,  76.7,  -0.1],
                 [  0.0, -99.0,  20.1,  -2.0,  64.7, -64.1],
                 [ -0.6, -99.0, -54.4,   0.0,  57.9,   0.1],
                ]
sb = vrepbot.VRepBot(cfg)

for tg in target_states:
    cfg.mprim.target_states = tg
    sb.m_prim = prims.create_mprim(cfg.mprim.name, cfg)

    order = (0.0, 0.0, 0.20)*cfg.mprim.n_basis*6
    sb.execute_order(order)
    print(np.mean([sb.channels['tip_pos'][-50:]], axis=1))

sb.c,lose()


# R,esult
# [[ 0.1100481 ,  0.6823279 ,  2.45170567]
#  [ 1.51487219,  2.00143284,  2.44584283]
#  [-1.10360631,  0.93663345,  2.40484004]
#  [-0.09994282,  1.55935965,  1.30536744]
#  [-0.01479483,  1.66135542,  3.49237228]
#  [ 1.79359275,  0.19804134,  0.45459374]
#  [ 0.0395507 ,  4.13089959,  3.17526394]
#  [-1.34310143, -0.06096789,  1.13319259]
#  [-0.03732515, -0.01554558, -0.3294154 ]
#  [ 0.00578956,  1.94747721, -1.36991427]]