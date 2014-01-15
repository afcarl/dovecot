import treedict
import random

import env
from surrogates.vrepsim import vrepbot

cfg = treedict.TreeDict()
cfg.vrep.ppf = 10

cfg.sprims.names = ['push']
cfg.sprims.uniformze = False

cfg.mprim.name = 'dmp1g'
cfg.mprim.motor_steps = 500 
cfg.mprim.max_steps = 1000
cfg.mprim.uniformze = False

vrepb = vrepbot.VRepBot(cfg)
order = tuple(random.uniform(a, b) for a, b in vrepb.m_bounds)
vrepb.execute_order(order)