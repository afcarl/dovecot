import forest

import dotdot
from dovecot import desc

cfg0 = desc._copy(deep=True)

cfg0.execute.partial_mvt = False
cfg0.execute.prefilter  = True

cfg0.mprim.dt = 0.01

cfg0.execute.check_self_collisions = False
cfg0.execute.is_simulation	   = True

cfg0.execute.hard.verbose_com  = True
cfg0.execute.hard.verbose_dyn  = True
cfg0.execute.hard.powerswitch  = True

cfg0.execute.simu.headless     = False
cfg0.execute.simu.vglrun       = False
cfg0.execute.simu.ppf          = 200
cfg0.execute.simu.load         = True
cfg0.execute.simu.mac_folder   = '/Applications/VRep/vrep.app/Contents/MacOS/' # only for mac
#cfg0.execute.simu.mac_folder  = '/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'

cfg0.sprims.names      = ['push']
cfg0.sprims.tip        = False
cfg0.sprims.uniformize = False
cfg0.sprims.scene      = 'center_cube'

cfg0.mprim.name        = 'dmpg25'
cfg0.mprim.motor_steps = 500
cfg0.mprim.max_steps   = 500
cfg0.mprim.uniformize  = False
cfg0.mprim.n_basis     = 2
cfg0.mprim.max_speed   = 400
cfg0.mprim.end_time    = 5.0

cfg0.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg0.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg0.mprim.angle_ranges  = ((110.0,  110.0), (99.0, 99.0), (99.0, 99.0), (120.0, 120.0), (99.0, 99.0), (99.0, 99.0))

cfg0.execute.simu.calibrdir = '~/.dovecot/tttcal/'

cfg1 = cfg0._copy(deep=True)
"""#TODO can't create new leaf 'scene' in a strict tree without a type or validation function declared"""
#cfg1.vrep.scene       = 'vrep_cylinder.ttt'
cfg1.sprims.names     = ['rollspin']
cfg1.sprims.scene     = 'cylinder'
