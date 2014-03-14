"""
Tests the collision detection system.
On random order, gives an estimation of the ratio between
executable and collision-prone orders, and assess the time
the collision detection is taking.
"""
from __future__ import division, print_function
import time
import random

import forest

import env
from surrogates.stemsim import stembot

import cfg

sb = stembot.StemBot(cfg.cfg0)

total   = 30
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

print((cfg.mprim.name, cfg.mprim.n_basis))
print("{}/{} reject, computed in {:.2f}s ({:.2f}s per executable order)".format(
        rejects, total, dur, dur/max(1, (total-rejects))))
