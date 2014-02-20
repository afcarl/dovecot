import numpy as np

from .. import prims
from . import vrepcom

from ..stemsim import stemcfg
from ..stemsim.collider import maycollide
from . import objscene

class OrderNotExecutableError(Exception):
    pass

class VRepBot(object):

    def __init__(self, cfg):
        self.cfg = cfg
        if 'angle_ranges' not in self.cfg.mprim:
            self.cfg.mprim.angle_ranges = ((110.0,  110.0), (99.0, 99.0), (99.0, 99.0), (120.0, 120.0), (99.0, 99.0), (99.0, 99.0))
        self.setup_prims()
        self.vrepcom = vrepcom.VRepCom(cfg,
                                       ppf        =cfg.vrep.ppf,
                                       vrep_folder=cfg.vrep.vrep_folder,
                                       load       =cfg.vrep.load)

        if cfg.sprims.prefilter:
            obj_scene = objscene.scenes[self.cfg.sprims.scene]
            self._collision_filter = maycollide.CollisionFilter(obj_scene.object_pos, obj_scene.object_geom, 11)

        self.OrderNotExecutableError = OrderNotExecutableError

    @property
    def m_feats(self):
        return self.m_prim.m_feats

    @property
    def m_bounds(self):
        return self.m_prim.m_bounds

    def setup_prims(self):
        self.s_prims = [prims.create_sprim(sprim_name, self.cfg) for sprim_name in self.cfg.sprims.names]
        self.m_prim = prims.create_mprim(self.cfg.mprim.name, self.cfg)
        self.context = {'x_bounds': (-3.0, 3.0),
                        'y_bounds': (-3.0, 3.0),
                        'z_bounds': ( 1.4, 3.3)}
        self.m_prim.process_context(self.context)
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

    def check_object_collision(self, motor_traj):
        #return True
        if self.cfg.sprims.prefilter:
            if not self._collision_filter.may_collide(motor_traj):
                return False
        return True

    def execute_order(self, order):
        motor_traj, max_steps = self.m_prim.process_order(order)
        motor_traj_2 = list(zip(*tuple(np.degrees(t_i[0]) for t_i in motor_traj)))
        if not self.check_object_collision(motor_traj_2):
            return (0.0,)*len(self.s_feats)
        sensors_data = self.vrepcom.run_simulation(motor_traj, max_steps)
        return self.process_sensors(*sensors_data)

    def close(self):
        self.vrepcom.close()