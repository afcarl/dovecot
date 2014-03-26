"""\
Get raw data from sensors out of V-Rep, ready to be processed by sensory primitives.
"""

from __future__ import print_function, division, absolute_import

from .. import prims

class VrepSensors(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.setup_sprims()

    def setup_sprims(self):
        self.s_prims = [prims.create_sprim(sprim_name, self.cfg) for sprim_name in self.cfg.sprims.names]
        self.context = {'x_bounds': (-300.0, 300.0),
                        'y_bounds': (-300.0, 300.0),
                        'z_bounds': ( 140.0, 330.0)}
        self.process_context()

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

    @property
    def null_feedback(self):
        return (0.0,)*len(self.s_feats)

    def process_sensors(self, object_sensors, joint_sensors, tip_sensors):

        #Construct sensors channels
        assert len(object_sensors) % (3+3+3+4) == 0
        n = int(len(object_sensors)/13)
        positions    = tuple(tuple(100.0*object_sensors[13*i   :13*i+ 3]) for i in range(n))
        quaternions  = tuple(tuple(      object_sensors[13*i+ 3:13*i+ 7]) for i in range(n))
        velocities_t = tuple(tuple(100.0*object_sensors[13*i+ 7:13*i+10]) for i in range(n))
        velocities_a = tuple(tuple(      object_sensors[13*i+10:13*i+13]) for i in range(n))

        self.channels = {}
        self.channels['object_pos']   = positions
        self.channels['object_ori']   = quaternions
        self.channels['object_vel_t'] = velocities_t
        self.channels['object_vel_a'] = velocities_a

        if self.cfg.sprims.tip:
            assert tip_sensors is not None
            n = int(len(tip_sensors)/3)
            tip_pos = tuple(tuple(tip_sensors[3*i:3*i+ 3]) for i in range(n))
            self.channels['tip_pos'] = tip_pos

        # Compute sensory primitives
        vals  = {}
        for sp in self.s_prims:
            feats  = sp.s_feats
            effect = sp.process_sensors(self.channels)
            for f_i, e_i in zip(feats, effect):
                assert f_i not in vals
                vals[f_i] = e_i

        return tuple(vals[f_i] for f_i in self.s_feats)
