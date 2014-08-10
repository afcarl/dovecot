from __future__ import print_function

from environments import tools

import dotdot
from dovecot.vrepsim import sim_env
from cfg import cfg0


cfg0.execute.simu.ppf = 1
cfg0.execute.simu.headless = False
cfg0.execute.prefilter     = False
cfg0.execute.check_self_collisions = True
cfg0.execute.scene.name = 'enormouscube0'

vrepb = sim_env.SimulationEnvironment(cfg0)

m_signals = [
             {'offset1.1': 18.21943132281342, 'offset1.0': -338.9672241670093, 'offset4.0': -397.8297109683216, 'offset4.1': 163.8139828390838, 'offset5.1': -130.2311110970922, 'offset5.0': 23.02622364874412, 'slope4.1': 39.10153799620025, 'slope4.0': -207.56986905246865, 'width0': 0.23436020919298378, 'width1': 0.30399572637750855, 'slope2.1': 396.2688102771226, 'offset3.1': -384.05478771928864, 'slope2.0': -126.1717466704136, 'slope3.0': 270.48508698026603, 'slope3.1': -317.7002945471223, 'offset2.0': -236.69870254908432, 'offset2.1': 320.6583707364009, 'slope0.1': -379.62428223776675, 'slope0.0': 199.06472087226064, 'slope1.0': 228.98425026951793, 'slope1.1': 264.0245367159629, 'offset0.0': -372.3667661134722, 'offset0.1': 289.1960053713341, 'offset3.0': 258.2975166795768, 'slope5.0': 377.35078460201737, 'slope5.1': 106.4133304061964},
            ]



for m_signal in m_signals*10:
    feedback = vrepb.execute(m_signal, meta={})
    s_vector = tools.to_vector(feedback['s_signal'], vrepb.s_channels)
    print(s_vector)
