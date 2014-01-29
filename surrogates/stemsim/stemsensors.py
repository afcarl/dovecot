class StemSensors(object):

    def setup_prims(self):
        self.s_prims = [prims.create_sprim(sprim_name, self.cfg) for sprim_name in self.cfg.sprims.names]
        self.m_prim = prims.create_mprim(self.cfg.mprim.name, self.cfg)
        self.context = {'x_bounds': (-3.0, 3.0),
                        'y_bounds': (-3.0, 3.0),
                        'z_bounds': ( 1.4, 3.3)}
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

    def process_sensors(self, object_sensors, joint_sensors, tip_sensors):

        # Construct sensors channels
        # assert len(object_sensors) % (3+3+3+4) == 0
        # n = int(len(object_sensors)/13)
        # positions    = tuple(tuple(object_sensors[13*i   :13*i+ 3]) for i in range(n))
        # quaternions  = tuple(tuple(object_sensors[13*i+ 3:13*i+ 7]) for i in range(n))
        # velocities_t = tuple(tuple(object_sensors[13*i+ 7:13*i+10]) for i in range(n))
        # velocities_a = tuple(tuple(object_sensors[13*i+10:13*i+13]) for i in range(n))

        # channels = {}
        # channels['object_pos']   = positions
        # channels['object_vel_t'] = velocities_t
        # channels['object_vel_a'] = velocities_a
        # channels['object_ori']   = quaternions

        assert len(object_sensors) % (3+4) == 0
        n = int(len(object_sensors)/7)
        positions    = tuple(tuple(object_sensors[7*i   :7*i+ 3]) for i in range(n))
        quaternions  = tuple(tuple(object_sensors[7*i+ 3:7*i+ 7]) for i in range(n))

        self.channels = {}
        self.channels['object_pos']   = positions
        self.channels['object_ori']   = quaternions

        if self.cfg.sensors.tip:
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
