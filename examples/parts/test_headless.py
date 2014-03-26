from __future__ import print_function

import sys
import random
random.seed(3344242)
import time

import forest

import env
from dovecot.vrepsim import vrepbot
from cfg import cfg0

cfg0.vrep.headless = True

if __name__ == "__main__":
    vrepb = vrepbot.VRepBot(cfg0)

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