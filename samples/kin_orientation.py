import testenv
from toolbox import gfx

import kinsim

def kin_orientation():
    """Test the orientation of each joint of the simulation"""

    vs = kinsim.KinSim()
    order = [0.0 for _ in range(6)]
    effect = vs.forward_kin(order)
    print(gfx.ppv(effect, fmt='+7.2f'))

    for i in range(6):
        order2 = list(order)
        order2[i] += 0.1
        effect = vs.forward_kin(order2)
        print(gfx.ppv(effect, fmt='+7.2f'))

#        print(', '.join('{:+6.2f}'.format(e) for e in effect))


kin_orientation()
