from __future__ import division, print_function
import time
import random

import treedict

import env
from surrogates.stemsim import stembot

cfg = treedict.TreeDict()

cfg.stem.dt = 0.01
cfg.stem.uid = 0
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.stem.motor_range = [01, 06]

cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 1
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.25

cfg.mprim.init_states   = [-30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [ 30.0, 0.0, 0.0, 0.0, 0.0, 0.0]

sb = stembot.StemBot(cfg)

total   = 10
rejects = 0
start = time.time()

for i in range(total):
    order = tuple(random.uniform(lb, hb) for lb, hb in sb.m_bounds)
    try:
        sb.create_trajectory(order)
    except stembot.CollisionError:
        rejects += 1

dur = time.time() - start
sb.close(rest=False)

print("{}/{} reject, computed in {:.2f}s ({:.2f}s per executable order)".format(
        rejects, total, dur, dur/max(1, (total-rejects))))
