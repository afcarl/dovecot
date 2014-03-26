from __future__ import print_function

import sys
import random
import time

import forest

import env
from dovecot.vrepsim import vrepbot
from cfg import cfg

cfg.vrep.ppf  = 200
cfg.vrep.vrep_folder='/Applications/V-REP/v_rep/bin/'
cfg.vrep.load = True
cfg.vrep.headless = True

total = int(sys.argv[1])

vrepb = vrepbot.VRepBot(cfg)

cols = 0
col_orders = []

start = time.time()
for i in range(total):
    order = tuple(random.uniform(a, b) for a, b in vrepb.m_bounds)
    effect = vrepb.execute_order(order)
    print(effect)
    if effect[2] != 0.0:
        cols += 1
        col_orders.append(order)
    print('{}({})/{}'.format(i+1, cols, total), end='\r')
    sys.stdout.flush()
    #print(' '.join('{:5.2f}'.format(e) for e in effect))

dur = time.time()-start
print('\nran for {}s ({:4.2f}s per order)'.format(int(dur), dur/total))
print('collisions : {}/{} ({:5.2f}%)'.format(cols, total, 100.0*cols/total))

#print('\ncolliding order:')
#print(col_orders)