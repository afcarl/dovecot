from __future__ import division, print_function
import forest
import time

import env
from dovecot.stemsim import stemcom
from cfg import cfg0

cfg = forest.Tree()
cfg._branch('stem')
cfg.stem._update(cfg0.stem)

sc = stemcom.StemCom(cfg)

start = time.time()
sc.setup([0.0]*6)
dur = time.time() - start

print("took {:.1f}s".format(dur))

sc.rest()
