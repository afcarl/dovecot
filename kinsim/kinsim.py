import numpy as np

import kin

class KinSim(object):

    def __init__(self):

        self.mfeats  = tuple(range(-13, 0))
        self.mbounds = ((-2.61799388, 2.61799388),)*12 + ((0.0, 2*2.61799388),)

        self.sfeats  = tuple(range(3))
        self.sbounds = ((-10.0, 10.0),)*3

    def execute_order(self, order):
        pose0 = np.array(order[0:6])
        pose1 = np.array(order[6:12])

        for i in range(10):
            pose = (pose0*(9-i) + i*pose1)/9.0
            tip = kin.forward_kin(*pose)

        return tip


if __name__ == "__main__":

    order = [0.0 for _ in range(13)]
    order[6] += 0.1
    ks = KinSim()
    print ks.execute_order(order)