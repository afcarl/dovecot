from __future__ import print_function, division
import os
import math

from ..ext.dynamics.fwdkin import fcls
from .stem_bodytree import bt

fs = fcls.FclSpace()
for body in bt.bodies():
    fs.register_body(body)


class CollisionError(Exception):
    pass


# should be a class, but no time
def collide(angles):

    orientation = [  1,  -1,  -1,   1,   1,   1]
    baseline    = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    #baseline    = [172, 150, 150, 172, 150, 150]
    u_angles = [o_i*(p_i-b_i) for p_i, b_i, o_i in zip(angles, baseline, orientation)]
    r_angles = [math.radians(a) for a in u_angles]

    bt.update(r_angles)
    c = fs.collisions()
    return c
