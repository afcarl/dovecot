from __future__ import print_function, division
import sys, time, os
import math

import pydyn

import env
from surrogates.stemsim import collider
from surrogates.stemsim import stemcfg
from surrogates.stemsim.collider import stem_bodytree
from surrogates.stemsim.collider import display

scfg = stemcfg.stems[int(sys.argv[1])]
stem = pydyn.MotorSet(serial_id=scfg.serial_id, motor_range=scfg.motorid_range, verbose=True)
stem.zero_pose = scfg.zero_pose

btdisplay = display.BodyTreeCubes(stem_bodytree.bt)

def update():

    orientation = [  1,  -1,  -1,   1,   1,   1]
    u_angles = [o_i*p_i for p_i, o_i in zip(list(stem.pose), orientation)]
    r_angles = [math.radians(a) for a in u_angles]

    if os.uname()[0] == 'Linux':
        btdisplay.green()
        contacts = collider.collide(stem.pose)
        for c in contacts:
            btdisplay.cubes_map[c[1].meta].collides = True
            btdisplay.cubes_map[c[2].meta].collides = True
    else:
        stem_bodytree.bt.update(r_angles)

btdisplay.add_update_function(update)

btdisplay.setup()
btdisplay.run()
