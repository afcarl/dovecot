import testenv
from toolbox import gfx

import treedict
from surrogates import vrepsim

def vrep_object():
    """Test the orientation of each joint of the simulation"""

    cfg = treedict.TreeDict()
    vs = vrepsim.VRepSim(cfg)

    order  = [0.0, 30.0,-80.0, 0.0, 50.0, 0.0]
    order += [0.0, 10.0,-74.0, 0.0, 64.0, 0.0]
    order += [0.0]
    effect = vs.execute_order(order)
    print(gfx.repr_vector(effect, fmt='+7.4f'))


vrep_object()