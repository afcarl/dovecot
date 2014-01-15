from .. import prims
from . import vrepcom

class VRepBot(object):

    def __init__(self, cfg):
        self.s_prims = [prims.create_sprim(sprim_name, cfg) for sprim_name in cfg.sprims.names]
        self.m_prim = prims.create_mprim(cfg.mprim.name, cfg)
        self.context = {'x_bounds': (-3.0, 3.0), 
                        'y_bounds': (-3.0, 3.0), 
                        'z_bounds': ( 1.4, 3.3)}
        self.process_context()
        self.vrepcom = vrepcom.VRepCom(ppf=cfg.vrep.ppf)

    @property
    def m_feats(self):
        return self.m_prim.m_feats

    @property
    def m_bounds(self):
        return self.m_prim.m_bounds

    def process_context(self):
        for sp in self.s_prims:
            sp.process_context(self.context)

        self.s_feats  = tuple()
        self.s_bounds = tuple()
        self.s_fixed  = tuple()
        self.s_units  = tuple()
        self.real_s_bounds = tuple()
        for sp in self.s_prims:
            self.s_feats  += sp.s_feats
            self.s_bounds += sp.s_bounds
            self.s_fixed  += sp.s_fixed
            self.s_units  += sp.s_units
            self.real_s_bounds += sp.real_s_bounds

    def process_sensors(self, object_sensors, joint_sensors):
        
        # Construct sensors channels
        assert len(object_sensors) % (3+3+3+4) == 0
        n = int(len(object_sensors)/13)
        positions   = tuple(tuple(object_sensors[13*i  :13*i+ 3]) for i in range(n))
        velocities  = tuple(tuple(object_sensors[13*i+3:13*i+ 6]) for i in range(n))
        velocities  = tuple(tuple(object_sensors[13*i+6:13*i+ 9]) for i in range(n))
        quaternions = tuple(tuple(object_sensors[13*i+9:13*i+13]) for i in range(n))

        channels = {}
        channels['object_pos'] = positions
        channels['object_vel'] = velocities
        channels['object_ori'] = quaternions

        # Compute sensory primitives
        vals  = {}
        for sp in self.s_prims:
            feats  = sp.s_feats
            effect = sp.process_sensors(channels)
            for f_i, e_i in zip(feats, effect):
                assert f_i not in vals
                vals[f_i] = e_i

        return tuple(vals[f_i] for f_i in self.s_feats)

    def execute_order(self, order):
        print(order)
        motor_traj, max_steps = self.m_prim.process_order(order)
        sensors_data = self.vrepcom.run_simulation(motor_traj, max_steps)
        return self.process_sensors(*sensors_data)
