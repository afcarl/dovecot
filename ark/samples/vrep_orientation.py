import testenv
from surrogates import vrepsim

def vrep_orientation():
    """Test the orientation of each joint of the simulation"""

    vs = vrepsim.VRepSim(objname = 'tip')
    order = [0.0 for b_min, b_max in vs.mbounds]
    effect = vs.execute_order(order)
    print(', '.join('{:+6.2f}'.format(e) for e in effect))

    for i in range(6):
        order2 = list(order)
        order2[6+i] += 50.0
        effect = vs.execute_order(order2)
        print(', '.join('{:+6.2f}'.format(e) for e in effect))


vrep_orientation()
