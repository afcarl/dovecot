from __future__ import print_function

import sys
import random
import time

import forest

import dotdot
from dovecot.vrepsim import sim_env
from cfg import cfg0

from environments import tools

cfg0.execute.simu.ppf = 1
cfg0.execute.simu.mac_folder='/Applications/VRep/vrep.app/Contents/MacOS/'
cfg0.execute.simu.load     = True
cfg0.execute.simu.headless = True
cfg0.execute.prefilter     = False
cfg0.execute.check_self_collisions = True

total = 1
if len(sys.argv) >= 2:
    total = int(sys.argv[1])


def memory_usage():
    import resource
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem


vrepb = sim_env.SimulationEnvironment(cfg0)

cols = 0
col_orders = []

start = time.time()
for i in range(total):
    print('{}: {:.2f} MiB'.format(i, memory_usage()))

    # if i == 100 or i == total-1:
    #     import pdb; pdb.set_trace()
    m_signal = tools.random_signal(vrepb.m_channels)
    feedback = vrepb.execute(m_signal, meta={})
    s_vector = tools.to_vector(feedback['s_signal'], vrepb.s_channels)
    if s_vector[2] != 0.0:
        cols += 1
        col_orders.append(m_signal)
#    print('{}({})/{}'.format(i+1, cols, total), end='\r')
    sys.stdout.flush()
    #print(' '.join('{:5.2f}'.format(e) for e in effect))

dur = time.time()-start
print('\nran for {}s ({:4.2f}s per order)'.format(int(dur), dur/total))
print('collisions : {}/{} ({:5.2f}%)'.format(cols, total, 100.0*cols/total))

#print('\ncolliding order:')
#print(col_orders)
