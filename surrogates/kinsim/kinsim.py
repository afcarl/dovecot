import math
import numpy as np

import robots

import kin


object_center = (+107.46,   +0.00, +212.05)
object_edge   = (+100.83,   +0.00, +209.25)

def distance(a, b):
    return math.sqrt(sum((a_i-b_i)*(a_i-b_i) for a_i, b_i in zip(a, b)))

class KinSim(robots.Robot):

    def __init__(self, cfg):
        self.cfg = cfg

        self.m_feats  = tuple(range(-13, 0))
        self.m_bounds = ((-100.0, 100.0),)*5 + ((-60.0, 60.0),)
        self.m_bounds = self.m_bounds*2 + ((0, 300.0),)

        self.s_feats  = tuple(range(4))
        self.s_bounds = ((-300.0, 200.0), (-300.0, 250.0), (-150.0, 350.0), (0.0, 1.0))

        self.object_radius = distance(object_center, object_edge)

        self.res = cfg.get('interpol_res', 10) # interpolation resolution

    def forward_kin(self, order):
        assert len(order) == 6
        return kin.forward_kin(*order)

    def _execute_order(self, order, **kwargs):
        pose0 = np.array(order[0:6])
        pose1 = np.array(order[6:12])

        object_pos = object_center
        collision = False
        #steps = []
        for i in range(self.res):
            pose = (pose0*(self.res-1-i) + i*pose1)/(self.res-1)
            tip = kin.forward_kin(*pose)
            if not collision and distance(tip, object_center) < self.object_radius:
                collision = True

        if collision:
            return tuple(tip) + (1.0,)
        else:
            return tuple(object_center)+(0.0,)


if __name__ == "__main__":

    order = [0.0 for _ in range(13)]
    order[6] += 0.1
    ks = KinSim()
    print ks.execute_order(order)
