from __future__ import print_function, division

import numpy as np
import os
import math

from toolbox import dist
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

        self.min_d_sq = 1.25*(obj_radius + marker_radius)**2
        self.obj_pos = obj_pos
        self.stem_model = smodel.SymbolicModel.from_file(os.path.abspath(os.path.join(__file__, '..')) + '/' + 'stem.smodel')

        self._u = np.matrix([[0], [0], [0], [1]])

    def may_collide(self, poses):
        for pose in poses:
            tip_pos = self.tip(pose)
            if dist(tip_pos, self.obj_pos) < self.min_d_sq:
                return True
        return False

    def tip(self, pose):
        tip = self.stem_model.f(*pose)*self._u
        return (tip[0, 0], tip[1, 0], tip[2, 0])

