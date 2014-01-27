from __future__ import division, print_function
import treedict

import env
from surrogates.stemsim import stemcom

cfg = treedict.TreeDict()
cfg.stem.dt = 0.01
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.stem.motor_range = [01, 50]


sc = stemcom.StemCom(cfg)

print("pos: [{}]".format(', '.join('{:.1f}'.format(p) for p in sc.pose)))