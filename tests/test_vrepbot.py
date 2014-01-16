from __future__ import print_function

import sys
import random
import time

import treedict

import env
from surrogates.vrepsim import vrepbot

cfg = treedict.TreeDict()
cfg.vrep.ppf = 10

cfg.sprims.names = ['push']
cfg.sprims.uniformze = False

cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 1500 
cfg.mprim.max_steps   = 1500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis = 2

cfg.mprim.init_states   = [-30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [ 30.0, 0.0, 0.0, 0.0, 0.0, 0.0]


vrepb = vrepbot.VRepBot(cfg)

total = 300
cols = 0
col_orders = []

start = time.time()
for i in range(total):
    order = tuple(random.uniform(a, b) for a, b in vrepb.m_bounds)
    effect = vrepb.execute_order(order)
    if effect != (0.0, 0.0, 0.0):
        cols += 1
        col_orders.append(order)
    print('{}({})/{}'.format(i+1, cols, total), end='\r')
    sys.stdout.flush()
    #print(' '.join('{:5.2f}'.format(e) for e in effect))

dur = time.time()-start
print('\nran for {}s ({:4.2f}s per order)'.format(int(dur), dur/total))
print('collisions : {}/{} ({:5.2f}%)'.format(cols, total, 100.0*cols/total))

print('\ncolliding order:')
print(col_orders)