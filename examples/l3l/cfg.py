import treedict

cfg = treedict.TreeDict()

cfg.stem.dt = 0.01

cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.hide_vrep = True

cfg.sprims.names     = ['push']
cfg.sprim.tip        = False
cfg.sprims.uniformze = False
cfg.sprims.prefilter.active = False
cfg.sprims.scene     = 'cube'


cfg.mprim.name = 'dmpg25'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.15

cfg.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]