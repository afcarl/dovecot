import testenv
from toolbox import gfx

import vrepsim

def vrep_object():
    """Test the orientation of each joint of the simulation"""

    vs = vrepsim.VRepSim(objname = 'marker')

    # order  = [0.0, 30.0,-80.0, 0.0, 50.0, 0.0]
    # order += [0.0, 10.0,-70.0, 0.0, 60.0, 0.0]
    # order += [0.0]
    # effect = vs.execute_order(order)
    # print(gfx.repr_vector(effect, fmt='+7.4f'))

    order  = [0.0, 30.0,-80.0, 0.0, 50.0, 0.0]
    order += [0.0, 10.0,-74.0, 0.0, 64.0, 0.0]
    order += [0.0]
    effect = vs.execute_order(order)
    print(gfx.repr_vector(effect, fmt='+7.4f'))


vrep_object()