from __future__ import print_function, division
import sys, time, os
import math

import dovecot.ext.pydyn

import dotdot
import dovecot
from dovecot.stemsim import stemcfg
from dovecot.stemsim import stemcom
from dovecot.collider import stem_bodytree
from dovecot.collider import display
from dovecot.collider import collider

from cfg import cfg0

if len(sys.argv) >= 2:
    uid = int(sys.argv[1])
else:
    uid = dovecot.stem_uid()

cfg0.execute.hard.uid = uid
sc = stemcom.StemCom(cfg0)

btdisplay = display.BodyTreeCubes(stem_bodytree.bt)

def update():

    orientation = [  1,  -1,  -1,   1,   1,   1]
    u_angles = [o_i*p_i for p_i, o_i in zip(list(sc.ms.pose), orientation)]
    r_angles = [math.radians(a) for a in u_angles]

    if os.uname()[0] == 'Linux':
        btdisplay.green()
        contacts = collider.collide(sc.ms.pose)
        for c in contacts:
            btdisplay.cubes_map[c[1].meta].collides = True
            btdisplay.cubes_map[c[2].meta].collides = True
    else:
        stem_bodytree.bt.update(r_angles)

btdisplay.add_update_function(update)

btdisplay.setup()
btdisplay.run()
