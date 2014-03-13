import forest

cfg = forest.Tree()
cfg._branch('stem')
cfg._branch('vrep')
cfg._branch('mprim')
cfg._branch('sprims')
cfg._branch('calib')

cfg.stem.dt = 0.01

cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.vrep.headless    = False
cfg.vrep.vglrun      = False
cfg.vrep.ppf         = 1
cfg.vrep.scene       = 'vrep_center.ttt'

cfg.sprims.names     = ['push']
cfg.sprim.tip        = False
cfg.sprims.uniformze = False
cfg.sprims.prefilter = False
cfg.sprims.scene     = 'cube_center'

cfg.mprim.name        = 'dmpg25'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.15

cfg.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

cfg.calib_datas_folder = '~/l2l-files/'

cfg2 = cfg._copy(deep=True)
cfg2.vrep.scene       = 'vrep_cylinder.ttt'
cfg2.sprims.names     = ['rollspin']
cfg2.sprims.scene     = 'cylinder'
