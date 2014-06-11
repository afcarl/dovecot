from __future__ import division, print_function
import time
import random
import sys

from environments import tools

import dotdot
import dovecot
import cfg

DEBUG = False

cfg_run = cfg.cfg0
cfg_run.mprim.n_basis = 2
cfg_run.execute.is_simulation = False
cfg_run.execute.hard.uid = int(sys.argv[1])

if DEBUG:
    cfg_run.vrep.headless = False
    cfg_run.vrep.ppf = 1

n = 1 if len(sys.argv) <= 2 else int(sys.argv[2])

start_time = time.time()
he = dovecot.HardwareEnvironment(cfg_run)

for _ in range(n):
    done = False
    while not done:
        try:
            m_signal = tools.random_signal(he.m_channels)
            feedback = he.execute(m_signal)
            done = True
        except he.OrderNotExecutableError:
            pass

he.close()
dur = time.time() - start_time

print("{} movements, {:.1f}s ({:.1f}s per movements)".format(n, dur, dur/n))
