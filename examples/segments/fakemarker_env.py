from __future__ import print_function

import sys
import random
import time

import scicfg

import dotdot
from dovecot.ext.toolbox import gfx
from dovecot import objdesc
from dovecot.vrepsim import sim_env
from cfg import cfg0 as vrep_cfg

from environments import tools


random.seed(0)

# Motor Simulation Environment
vrep_cfg.sprims.names = ['push']
vrep_cfg.sprims.tip   = True
vrep_cfg.execute.is_simulation         = True
vrep_cfg.execute.simu.ppf              = 1
vrep_cfg.execute.simu.headless         = False
vrep_cfg.execute.prefilter             = False #True
vrep_cfg.execute.check_self_collisions = True
vrep_cfg.execute.scene.objects.cube45.pos = (-60.0, 0.0, None)

vrep_env = sim_env.SimulationEnvironment(vrep_cfg)

#m_signal = tools.random_signal(vrep_env.m_channels)
m_signal = {'slope0.1': 359.80220393397553, 'slope0.0': -227.81079906822575, 'offset4.0': -85.7103889189296, 'offset4.1': -25.735420066496204, 'offset5.1': -186.64161337701435, 'offset5.0': 157.0433582394495, 'slope4.1': -244.44695404573906, 'slope4.0': -191.67123103619278, 'width0': 0.19268932673260142, 'width1': 0.27615834483064006, 'offset3.1': -300.869431663208, 'slope2.1': -109.65384632030873, 'slope2.0': -259.3317003038468, 'slope3.0': -187.35635728906493, 'slope3.1': 61.61756391254147, 'offset2.0': 325.40075250529753, 'offset2.1': -32.73063038339836, 'offset1.1': -122.72243322237546, 'offset1.0': -71.7020756097541, 'slope1.0': -331.5353644241496, 'slope1.1': -324.04964527689754, 'offset0.0': -164.97949641297245, 'offset0.1': 78.94129803114015, 'offset3.0': -12.092508496067978, 'slope5.0': 13.867818190007483, 'slope5.1': 133.3742478782948}
m_signal = {'slope0.1': 286.28651126262582, 'slope0.0': 361.86675289573463, 'offset4.0': -292.89216625306716, 'offset4.1': -386.61263043899686, 'offset5.1': -97.859191311508482, 'offset5.0': 5.3179298744379366, 'slope4.1': -203.9711769515535, 'slope4.0': 219.49426622387966, 'width0': 0.16775078084659101, 'width1': 0.09448622082861588, 'offset3.1': -118.33301790237419, 'slope2.1': 19.243491637709212, 'slope2.0': 268.2515721669846, 'slope3.0': 334.79037411595436, 'slope3.1': -275.72374782794952, 'offset2.0': -70.963051108955653, 'offset2.1': 365.61510612198799, 'offset1.1': -277.95881848193881, 'offset1.0': -297.41210343219825, 'slope1.0': 112.50366790639589, 'slope1.1': -38.221724344275458, 'offset0.0': -307.34408432197557, 'offset0.1': 182.71390994161243, 'offset3.0': 201.52578922191412, 'slope5.0': -315.39699964305294, 'slope5.1': 126.57810917846086}
#m_signal = {'slope0.1': 298.09827156001427, 'slope0.0': 79.652956473864151, 'offset4.0': -162.41210293517642, 'offset4.1': 109.49900798972533, 'offset5.1': -175.42498845615094, 'offset5.0': -160.26596298026982, 'slope4.1': 171.79141657363357, 'slope4.0': -274.29517238030542, 'width0': 0.1435977092967371, 'width1': 0.17356864122584356, 'offset3.1': -186.15766986357559, 'slope2.1': -276.32846375583802, 'slope2.0': -296.63872325766863, 'slope3.0': 329.00446615901274, 'slope3.1': -169.19864925722985, 'offset2.0': 250.843202060718, 'offset2.1': -78.758125413260132, 'offset1.1': -138.77216183846519, 'offset1.0': -351.07111653953416, 'slope1.0': 133.59253889704155, 'slope1.1': -137.77400774139073, 'offset0.0': -322.94341122802507, 'offset0.1': -193.6504864237107, 'offset3.0': 283.42401369233596, 'slope5.0': -340.65603029711804, 'slope5.1': 109.23277816754353}
m_signal = {'slope0.1': 211.31776065122483, 'slope0.0': -48.089030853817349, 'offset4.0': -305.57185871029378, 'offset4.1': 107.71054739766146, 'offset5.1': 295.64969876482257, 'offset5.0': 246.51358421412488, 'slope4.1': -319.31496020716361, 'slope4.0': 89.584125360959092, 'width0': 0.092062389208790757, 'width1': 0.06485087878036716, 'offset3.1': 26.727411279564592, 'slope2.1': -282.05791218907177, 'slope2.0': -131.33893431806734, 'slope3.0': 34.293624163320601, 'slope3.1': -73.788273632193466, 'offset2.0': -231.23990247180441, 'offset2.1': -299.81144381972115, 'offset1.1': -283.35223261010412, 'offset1.0': -399.96166737535157, 'slope1.0': 31.855970828767965, 'slope1.1': -230.23596958294024, 'offset0.0': -178.7995271682712, 'offset0.1': -52.349600749468891, 'offset3.0': -337.39937436407786, 'slope5.0': 75.635437724675626, 'slope5.1': 210.36668763083208}
m_signal = {'slope0.1': 190.50007020934845, 'slope0.0': 199.50958228875788, 'offset4.0': -7.804807100399728, 'offset4.1': -240.07526874538954, 'offset5.1': -163.42168617939717, 'offset5.0': -177.0814778611401, 'slope4.1': 158.9595062415451, 'slope4.0': -141.64499199408039, 'width0': 0.17498410992161906, 'width1': 0.18482871816713167, 'offset3.1': 57.322726165151835, 'slope2.1': -220.46675276703613, 'slope2.0': -225.09555831454574, 'slope3.0': 163.82172821538666, 'slope3.1': -359.39232410734985, 'offset2.0': -83.60386879657204, 'offset2.1': -45.05175463122163, 'offset1.1': 75.49928548590276, 'offset1.0': -317.19341947693215, 'slope1.0': 42.505948966624715, 'slope1.1': -136.72390201007295, 'offset0.0': -204.6329174553664, 'offset0.1': -238.92817744079906, 'offset3.0': 154.5993404190857, 'slope5.0': -186.83767790077522, 'slope5.1': 171.8761882702512}

# {'slope0.1': 315.971868333958, 'slope0.0': 356.8184838976531, 'offset4.0': -147.00441901822137, 'offset4.1': -175.00618864226584, 'offset5.1': -151.6421529672196, 'offset5.0': -392.5183115862228, 'slope4.1': 340.2022482469458, 'slope4.0': -225.21258048261953, 'width0': 0.4780400291212285, 'width1': 0.31724360361737886, 'offset3.1': -176.159312934924, 'slope2.1': 243.6458962649599, 'slope2.0': 307.12538181667185, 'slope3.0': 31.285973746327045, 'slope3.1': -51.35630177069919, 'offset2.0': -196.16313176734232, 'offset2.1': 85.93167722899165, 'offset1.1': 20.115107982782376, 'offset1.0': -277.2003967011555, 'slope1.0': -160.2523857430744, 'slope1.1': -275.94757738049145, 'offset0.0': -165.62057389086763, 'offset0.1': -301.89714524561106, 'offset3.0': 328.5699713907246, 'slope5.0': -44.42212498017949, 'slope5.1': 334.36474321990875}
# 0086 {'y': -10.90446412563324, 'x': 10.734552145004272, 'push_saliency': 1000.0} [recorded]
# 500
#      {'y': -7.6036453247070312, 'x': 15.024757385253906, 'push_saliency': 1000.0}
# {'slope0.1': -83.02041898345698, 'slope0.0': 85.47918303830073, 'offset4.0': -111.32730487047871, 'offset4.1': -366.6740769762057, 'offset5.1': 299.67744082397326, 'offset5.0': -261.8987181474696, 'slope4.1': 299.9968055632719, 'slope4.0': 203.09597877643034, 'width0': 0.02673876219898871, 'width1': 0.06841799977515968, 'offset3.1': 243.69212366675447, 'slope2.1': 396.04267129498135, 'slope2.0': 145.56783970841173, 'slope3.0': -330.82158291506846, 'slope3.1': -92.00051687715154, 'offset2.0': -375.00947018524516, 'offset2.1': -307.31137185112516, 'offset1.1': -92.07759592052838, 'offset1.0': -31.832020356072576, 'slope1.0': -305.9008610505911, 'slope1.1': 179.9270036723509, 'offset0.0': -238.47898044796042, 'offset0.1': -133.24833546419035, 'offset3.0': 61.21103688143455, 'slope5.0': -280.45893964776997, 'slope5.1': -321.90771638544004}


#print(tools.to_vector(m_signal, vrep_env.m_channels))
feedback = vrep_env.execute(m_signal, meta={})
print('{}{}{}'.format(gfx.green, tools.to_vector(feedback['s_signal'], vrep_env.s_channels), gfx.end))


# No Object Environment
noobject_cfg = vrep_cfg._deepcopy()
noobject_cfg.execute.scene.objects.cube45.pos = (250.0, 250.0, None)
noobject_cfg.execute.simu.headless            = True
noobject_cfg.execute.simu.ppf                 = 200

noobject_env = sim_env.SimulationEnvironment(noobject_cfg)
meta = {}
feedback = noobject_env.execute(m_signal, meta=meta)
marker_traj = meta['log']['raw_sensors']['marker_sensors']
assert len(marker_traj) % 3 == 0
marker_traj = [(i*vrep_cfg.mprims.dt, marker_traj[3*i:3*(i+1)]) for i in range(int(len(marker_traj)/3))]

# Marker Simulation Environment
marker_cfg = vrep_cfg._deepcopy()
marker_cfg.execute.is_simulation = False

marker_env = sim_env.SimulationEnvironment(marker_cfg)
marker_env.vrepcom.run_simulation(marker_traj)

raw_input()
vrep_env.close(kill=True)
marker_env.close(kill=True)
