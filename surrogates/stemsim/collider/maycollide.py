from __future__ import print_function, division

import numpy as np
import os
import math

import toolbox
from toolbox import gfx
import dynamics.fwdkin.smodel as smodel

class CollisionFilter(object):
    """
        Given two objects (one static), tell if there is :
        - absolutely no possibility of collision
        - maybe a possibility
    """

    def __init__(self, obj_pos, obj_geom, marker_radius):
        if len(obj_geom) == 3: # cube
            obj_radius = math.sqrt(sorted(obj_geom)[2]**2 + sorted(obj_geom)[1]**2)

        self.min_d_sq = 1.2*((obj_radius + marker_radius)**2)
        self.obj_pos = obj_pos
        self.stem_model = smodel.SymbolicModel.from_file(os.path.abspath(os.path.join(__file__, '..')) + '/' + 'stem.smodel')

        self._u = np.matrix([[0], [0], [0], [1]])

    def may_collide(self, poses):
        for pose in poses:
            orientation = [1.0, -1.0, -1.0, 1.0, 1.0, 1.0]
            pose_r = [math.radians(p*o) for p, o in zip(pose, orientation)]
            tip_pos = self.tip(pose_r)
            # print(gfx.ppv(pose), gfx.ppv(tip_pos), gfx.ppv(self.obj_pos))
            # print('{:.1f} {:.1f}'.format(toolbox.dist_sq(tip_pos, self.obj_pos), self.min_d_sq))
            if toolbox.dist_sq(tip_pos, self.obj_pos) < self.min_d_sq:
                return True
        return False

    def tip(self, pose):
        tip = self.stem_model.f(*pose)*self._u
        return (tip[0, 0], tip[1, 0], tip[2, 0])

