import forest

import env
from dovecot import desc

cfg = desc._copy(deep=True)

cfg.execute.partial_mvt = False
cfg.execute.prefilter  = True

cfg.mprim.dt = 0.01

cfg.execute.check_self_collisions = False
cfg.execute.is_simulation	   = True

cfg.execute.hard.verbose_com  = True
cfg.execute.hard.verbose_dyn  = True
cfg.execute.hard.powerswitch  = True

cfg.execute.simu.headless     = False
cfg.execute.simu.vglrun       = False
cfg.execute.simu.ppf          = 200
cfg.execute.simu.load         = True
cfg.execute.simu.mac_folder   = '/Applications/VRep/vrep.app/Contents/MacOS/' # only for mac
#cfg.execute.simu.mac_folder  = '/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'

cfg.sprims.names      = ['push']
cfg.sprims.tip        = False
cfg.sprims.uniformize = False
cfg.sprims.scene      = 'center_cube'

cfg.mprim.name        = 'dmpg25'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformize  = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 400
cfg.mprim.end_time    = 5.0

cfg.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.angle_ranges  = ((110.0,  110.0), (99.0, 99.0), (99.0, 99.0), (120.0, 120.0), (99.0, 99.0), (99.0, 99.0))


cfg.execute.simu.calibrdir = '~/.dovecot/tttcal/'

cfg.logger.enabled = False
cfg.logger.write_delay = 10 # seconds
cfg.logger.folder = '~/.dovecot/logger/'
cfg.logger.filename = 'examples_'
cfg.logger.ignored = ['opti_traj', 'vrep_traj']

cfg1 = cfg._copy(deep=True)
"""#TODO can't create new leaf 'scene' in a strict tree without a type or validation function declared"""
#cfg1.vrep.scene       = 'vrep_cylinder.ttt'
cfg1.sprims.names     = ['rollspin']
cfg1.sprims.scene     = 'cylinder'
