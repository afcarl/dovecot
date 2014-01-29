from __future__ import division, print_function
import sys
import treedict

import env
from surrogates.stemsim import stemcom

cfg = treedict.TreeDict()
cfg.stem.uid = int(sys.argv[1])
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
sc = stemcom.StemCom(cfg)

print("pos: [{}]".format(', '.join('{:.1f}'.format(m.position) for m in sc.motors)))