import testenv
import sys

import treedict
from toolbox import gfx

from surrogates import vrepsim

def vrep_eval(order, n = 1):
    """Test the orientation of each joint of the simulation"""

    cfg = treedict.TreeDict()
    cfg.objectname = 'cube'
    vs = vrepsim.VRepSim(cfg)

    # order  = [0.0, 30.0,-80.0, 0.0, 50.0, 0.0]
    # order += [0.0, 10.0,-70.0, 0.0, 60.0, 0.0]
    # order += [0.0]
    # effect = vs.execute_order(order)
    # print(gfx.repr_vector(effect, fmt='+7.4f'))
    for _ in range(n):
        effect = vs.execute_order(order)
        color = gfx.green if effect[3] == 1.0 else gfx.red
        print('{} -> {}{}{}'.format(gfx.ppv(order, fmt='+7.2f'), color, gfx.ppv(effect, fmt='+7.4f'), gfx.end))


order = eval(sys.argv[1], {}, {})
if len(sys.argv) > 2:
    vrep_eval(order, n = int(sys.argv[2]))
else:
    vrep_eval(order)