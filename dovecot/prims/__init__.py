
sprims = {}

def create_sprim(name, cfg):
    sensory_class = sprims[name]
    sensory_prim = sensory_class(cfg)
    return sensory_prim


from .mprims import create_mprim

import s_push, s_roll
