from __future__ import print_function

import sys
import random
random.seed(3344242)
import time

import treedict

import env
from surrogates.vrepsim import vrepbot
from test_launch_vrep import cfg

cfg.vrep.headless = False

if __name__ == "__main__":
    vrepb = vrepbot.VRepBot(cfg)

    total = 10
    cols  = 0
    col_orders = []

    start = time.time()
    for i in range(total):
        order = tuple(random.uniform(a, b) for a, b in vrepb.m_bounds)
        effect = vrepb.execute_order(order)
        print(effect)
        print('{}/{} : {}'.format(i+1, total, effect))

    vrepb.close()