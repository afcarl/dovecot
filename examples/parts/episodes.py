from __future__ import division, print_function
import time
import random
import sys

import env
from dovecot.stemsim import episode
import cfg

DEBUG = False

cfg_run = cfg.cfg0
cfg_run.mprim.n_basis = 2
cfg_run.stem.uid  = int(sys.argv[1])

if DEBUG:
    cfg_run.vrep.headless = False
    cfg_run.vrep.ppf = 1

episodes_count  = 1 if len(sys.argv) <= 2 else int(sys.argv[2])
collisions      = 0

start_time = time.time()
ep = episode.Episode(cfg_run)

for _ in range(episodes_count):
    done = False
    while not done:
        try:
            order = tuple(random.uniform(lb, hb) for lb, hb in ep.m_bounds)
            effect = ep.execute_order(order)
            if effect[2] != 0.0:
                collisions += 1
            done = True
        except episode.OrderNotExecutableError:
            pass

ep.close()
dur = time.time() - start_time

print("{} movements, {} collisions ({:.1f}%), {:.1f}s ({:.1f}s per movements)".format(
    episodes_count, collisions, 100.0*collisions/episodes_count, dur, dur/episodes_count))
