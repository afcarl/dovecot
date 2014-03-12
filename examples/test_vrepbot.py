from __future__ import print_function

import sys
import random
import time

import forest

import env
from surrogates.vrepsim import vrepbot

cfg = forest.Tree()
cfg.vrep.ppf  = 10
cfg.vrep.vrep_folder='/Applications/V-REP/v_rep/bin/'
cfg.vrep.load = True
cfg.vrep.headless = False

cfg.sprims.names = ['push']
cfg.sprims.uniformze = False
cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.25

cfg.calib_datas_folder = '~/l2l-files/'

cfg.mprim.init_states   = [-30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [ 30.0, 0.0, 0.0, 0.0, 0.0, 0.0]

if __name__ == "__main__":
    vrepb = vrepbot.VRepBot(cfg)

    total = 10
    cols = 0
    col_orders = []

    start = time.time()
    for i in range(total):
        order = tuple(random.uniform(a, b) for a, b in vrepb.m_bounds)
        effect = vrepb.execute_order(order)
        print(effect)
        if effect[2] != 0.0:
            print(effect)
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