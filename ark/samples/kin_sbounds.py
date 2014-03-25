import testenv
import random
import forest

from toolbox import gfx
from surrogates import kinsim

def kin_sbounds():
    """Test the orientation of each joint of the simulation"""
    cfg = forest.Tree()
    cfg.interpol_res = 50

    vs = kinsim.KinSim(cfg)
    sb = [[float('inf'), -float('inf')] for _ in vs.s_bounds]

    for _ in range(1000000):
        order  = [random.uniform(lb, hb) for lb,
         hb in vs.m_bounds]
        effect = vs.execute_order(order)
        sb = [[min(e_i, sbmin_i), max(e_i, sbmax_i)] for e_i, (sbmin_i, sbmax_i) in zip(effect, sb)]

    print sb


kin_sbounds()
