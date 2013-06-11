import testenv
import vrepsim

def vrep_object():
    """Test the orientation of each joint of the simulation"""

    vs = vrepsim.VRepSim(objname = 'marker')
    #order  = [0.0 for b_min, b_max in vs.mbounds]
    order  = [0.0, 30.0,-80.0, 0.0, 50.0, 0.0]
    order += [0.0, 10.0,-70.0, 0.0, 60.0, 0.0]
    order += [0.0]
    effect = vs.execute_order(order)
    print(', '.join('{:+7.3f}'.format(e) for e in effect))


vrep_object()