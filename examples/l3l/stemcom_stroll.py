from __future__ import division, print_function
import treedict
import time

import env
from surrogates.stemsim import stemcom

cfg = treedict.TreeDict()
cfg.stem.dt = 0.01
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.stem.uid = 0

sc = stemcom.StemCom(cfg)

start = time.time()
sc.setup([0.0]*6)
dur = time.time() - start

print("took {:.1f}s".format(dur))

sc.rest()
