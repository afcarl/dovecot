import testenv
import random, sys

import treedict
from toolbox import gfx

from surrogates import vrepsim

def vrep_random(n = 1):
    """Test the orientation of each joint of the simulation"""

    cfg = treedict.TreeDict()
    cfg.objectname = 'cube'
    vs = vrepsim.VRepSim(cfg)

    # order  = [0.0, 30.0,-80.0, 0.0, 50.0, 0.0]
    # order += [0.0, 10.0,-70.0, 0.0, 60.0, 0.0]
    # order += [0.0]
    # effect = vs.execute_order(order)
    # print(gfx.repr_vector(effect, fmt='+7.4f'))
    collisions = 0
    for _ in range(n):
        order  = [random.uniform(-100.0, 100.0) for _ in range(12)] + [random.uniform(0.0, 100.0)]
        effect = vs.execute_order(order)
        if effect[3] == 1.0:
            collisions += 1
        color = gfx.green if effect[3] == 1.0 else gfx.red
        print('{} -> {}{}{}'.format(gfx.ppv(order, fmt='+7.2f'), color, gfx.ppv(effect, fmt='+7.4f'), gfx.end))

    return float(collisions)/n

if (sys.argv)>1:
    collision_ratio = vrep_random(int(sys.argv[1]))
    print("{}% collisions".format(collision_ratio))
else:
    vrep_random()
