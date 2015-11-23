""""""

from __future__ import division, print_function
import sys
import scicfg

import env
from dovecot.stemsim import stemcom

cfg = scicfg.SciConfig()
cfg._branch('stem')
cfg.stem.uid = int(sys.argv[1])
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
sc = stemcom.StemCom(cfg)

print("pos: [{}]".format(', '.join('{:.1f}'.format(p) for p in sc.ms.pose)))