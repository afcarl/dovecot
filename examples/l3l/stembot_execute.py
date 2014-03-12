from __future__ import division, print_function
import time
import random
import sys

import forest

import env
from surrogates.stemsim import stembot

cfg = forest.Tree()

cfg.stem.dt = 0.01
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.stem.uid = int(sys.argv[1])

cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.45

cfg.calib_datas_folder = '~/l2l-files/'

cfg.mprim.init_states   = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

sb = stembot.StemBot(cfg)

total = 50
count = 0

start = time.time()
while count < total:
    try:
        order = tuple(random.uniform(lb, hb) for lb, hb in sb.m_bounds)
        sb.execute_order(order)
        count += 1
    except stembot.CollisionError:
        pass
dur = time.time() - start
sb.close()

print("{} movements, {:.1f}s ({:.1f}s per movements)".format(total, dur, dur/total))
