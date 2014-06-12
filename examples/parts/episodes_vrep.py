from __future__ import print_function

import sys
import random
import time

import forest

import env
from dovecot.vrepsim import sim_env
from cfg import cfg0

from environments import tools

cfg0.execute.simu.ppf  = 200
cfg0.execute.simu.mac_folder='/Applications/VRep/vrep.app/Contents/MacOS/'
cfg0.execute.simu.load = True
cfg0.execute.simu.headless = True

total = 1
if len(sys.argv) >= 2:
    total = int(sys.argv[1])


vrepb = sim_env.SimulationEnvironment(cfg0)

cols = 0
col_orders = []

start = time.time()
for i in range(total):
    m_signal = tools.random_signal(vrepb.m_channels)
    feedback = vrepb.execute(m_signal, meta={})
    s_vector = tools.to_vector(feedback['s_signal'], vrepb.s_channels)
    if s_vector[2] != 0.0:
        cols += 1
        col_orders.append(m_signal)
    print('{}({})/{}'.format(i+1, cols, total), end='\r')
    sys.stdout.flush()
    #print(' '.join('{:5.2f}'.format(e) for e in effect))

dur = time.time()-start
print('\nran for {}s ({:4.2f}s per order)'.format(int(dur), dur/total))
print('collisions : {}/{} ({:5.2f}%)'.format(cols, total, 100.0*cols/total))

#print('\ncolliding order:')
#print(col_orders)
