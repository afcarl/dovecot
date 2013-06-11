import math
import numpy as np

import kin


object_center = (+107.46,   +0.00, +212.05)
object_edge   = (+100.83,   +0.00, +209.25)

def distance(a, b):
    return math.sqrt(sum((a_i-b_i)*(a_i-b_i) for a_i, b_i in zip(a, b)))

class KinSim(object):

    def __init__(self, res = 10):

        self.mfeats  = tuple(range(-13, 0))
        self.mbounds = ((-2.61799388, 2.61799388),)*12 + ((0.0, 2*2.61799388),)

        self.sfeats  = tuple(range(3))
        self.sbounds = ((-10.0, 10.0),)*3

        self.object_radius = distance(object_center, object_edge)

        self.res = res

    def forward_kin(self, order):
        assert len(order) == 6
        return kin.forward_kin(*order)

    def execute_order(self, order):
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
            return tip
        else:
            return object_center


if __name__ == "__main__":

    order = [0.0 for _ in range(13)]
    order[6] += 0.1
    ks = KinSim()
    print ks.execute_order(order)
