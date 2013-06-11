import testenv
import math

import numpy as np

from toolbox import gfx

import kinsim


def kin_object():
    """Test the orientation of each joint of the simulation"""

    vs = kinsim.KinSim()
    order = np.array([0.0, 10.0, -70.0, 0.0, 60.0, 0.0])/180.0*math.pi
    effect = vs.forward_kin(order)
    print(gfx.ppv(effect, fmt='+7.2f'))

    order = np.array([0.0, 10.0,-74.0, 0.0, 64.0, 0.0])/180.0*math.pi
    effect = vs.forward_kin(order)
    print(gfx.ppv(effect, fmt='+7.2f'))


kin_object()
