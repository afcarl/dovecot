from __future__ import division, print_function
import time
import random
import sys

import forest

import env
from dovecot.stemsim import stembot

from cfg import cfg0

cfg0.stem.uid = int(sys.argv[1])
sb = stembot.StemBot(cfg0, timeout=10)

total = 50
count = 0

start = time.time()
while count < total:
    try:
        order = tuple(random.uniform(lb, hb) for lb, hb in sb.m_bounds)
        sb.execute_order(order)
        count += 1
    except stembot.CollisionError:
        pass
dur = time.time() - start
sb.close()

print("{} movements, {:.1f}s ({:.1f}s per movements)".format(total, dur, dur/total))
