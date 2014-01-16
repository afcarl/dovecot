import treedict

cfg = treedict.TreeDict()
cfg.vrep.ppf = 200

cfg.sprims.names = ['push']
cfg.sprims.uniformze = False

cfg.mprim.name = 'dmp1g'
cfg.mprim.motor_steps = 500 
cfg.mprim.max_steps = 1000
cfg.mprim.uniformze = False

cfg.mprim.init_states   = [-30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [ 30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
