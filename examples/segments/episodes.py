from __future__ import division, print_function
import time
import random
import sys
import os

from environments import tools

import dotdot
import dovecot
import cfg


DEBUG = False

cfg_run = cfg.cfg0
cfg_run.mprim.n_basis = 2
cfg_run.execute.prefilter  = False
cfg_run.execute.is_simulation = False

if DEBUG:
    cfg_run.vrep.headless = False
    cfg_run.vrep.ppf = 1

n = 1 if len(sys.argv) <= 1 else int(sys.argv[1])
if len(sys.argv) >= 3:
    cfg_run.execute.hard.uid = int(sys.argv[2])

start_time = time.time()
he = dovecot.HardwareEnvironment(cfg_run)

def memory_usage():
    import resource
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem

for i in range(n):

    print('{}: {:.2f} MiB'.format(i, memory_usage()))
    # if i == n-1:
    #     import pdb
    #     pdb.set_trace()
    done = False
    while not done:
        try:
            m_signal = tools.random_signal(he.m_channels)
            #print(', '.join('{:.2f}'.format(m_i) for m_i in tools.to_vector(m_signal, he.m_channels)))
            feedback = he.execute(m_signal)
            done = True
        except he.OrderNotExecutableError:
            pass

he.close()
dur = time.time() - start_time

print("{} movements, {:.1f}s ({:.1f}s per movements)".format(n, dur, dur/n))
