import forest

cfg0 = forest.Tree()
cfg0._branch('stem')
cfg0._branch('vrep')
cfg0._branch('mprim')
cfg0._branch('sprims')
cfg0._branch('calib')

cfg0.partial_mvt = False

cfg0.stem.dt = 0.01

cfg0.stem.verbose_com = True
cfg0.stem.verbose_dyn = True
cfg0.vrep.headless    = False
cfg0.vrep.vglrun      = False
cfg0.vrep.ppf         = 1
cfg0.vrep.scene       = 'vrep_center.ttt'

cfg0.sprims.names     = ['push']
cfg0.sprims.tip       = False
cfg0.sprims.uniformze = False
cfg0.sprims.prefilter = False
cfg0.sprims.scene     = 'cube_center'

cfg0.mprim.name        = 'dmpg25'
cfg0.mprim.motor_steps = 500
cfg0.mprim.max_steps   = 500
cfg0.mprim.uniformze   = False
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
