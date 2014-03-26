import forest

import env
from dovecot.cfgdesc import desc

cfg0 = desc._copy(deep=True)

cfg0.partial_mvt = False

cfg0.stem.dt = 0.01

cfg0.stem.verbose_com  = True
cfg0.stem.verbose_dyn  = True
cfg0.vrep.headless     = True
cfg0.vrep.vglrun       = False
cfg0.vrep.ppf          = 200
cfg0.vrep.load         = True
cfg0.vrep.mac_folder   = '/Applications/V-REP/v_rep/bin' # only for mac
#cfg0.vrep.mac_folder  = '/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'

cfg0.sprims.names      = ['push']
cfg0.sprims.tip        = False
cfg0.sprims.uniformize = False
cfg0.sprims.prefilter  = False
cfg0.sprims.scene      = 'center_cube'

cfg0.mprim.name        = 'dmpg25'
cfg0.mprim.motor_steps = 500
cfg0.mprim.max_steps   = 500
cfg0.mprim.uniformize   = False
cfg0.mprim.n_basis     = 2
cfg0.mprim.max_speed   = 1.0
cfg0.mprim.end_time    = 1.15

cfg0.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg0.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

cfg0.vrep.calibrdir = '~/l2l-files/'

cfg1 = cfg0._copy(deep=True)
cfg1.vrep.scene       = 'vrep_cylinder.ttt'
cfg1.sprims.names     = ['rollspin']
cfg1.sprims.scene     = 'cylinder'
