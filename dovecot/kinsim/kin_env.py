from __future__ import print_function, division, absolute_import
import math

import environments

from ..vrepsim import sim_env
from ..collider import maycollide
from .. import prims
from .. import ttts


class KinEnvironment(sim_env.SimulationEnvironment):

    def __init__(self, cfg):
        environments.PrimitiveEnvironment.__init__(self, cfg)

        self.scene_name = self.cfg.execute.scene.name
        self.caldata = ttts.TTTCalibrationData(self.scene_name, self.cfg.execute.simu.calibrdir)
        self.caldata.load()

        obj_pos = self.cfg.execute.scene.object.pos
        assert obj_pos[0] is not None and obj_pos[1] is not None
        obj_pos = [o_i if o_i is not None else o2_i for o_i, o2_i in zip(obj_pos, self.caldata.position)]

        self.collider = maycollide.FakeColliderCube(self.cfg, obj_pos,
                                                    self.caldata.dimensions, self.MARKER_SIZE)

    def _create_primitives(self, cfg):
        self.context = {'x_bounds': (-300.0, 300.0),
                        'y_bounds': (-300.0, 300.0),
                        'z_bounds': (   0.0, 330.0)}

        # motor primitive
        self.m_prim = prims.create_mprim(self.cfg.mprims.name, self.cfg)
        self.m_prim.process_context(self.context)

        # sensory primitive
        self.s_prim = environments.ConcatSPrimitive()
        for sprim_name in self.cfg.sprims.names:
            sp = prims.create_sprim(sprim_name, self.cfg)
            sp.process_context(self.context)
            self.s_prim.add_s_prim(sp)


    def _execute_raw(self, motor_command, meta=None):

        motor_traj = motor_command

        meta['log'] = {}

        motor_poses = self._trajs2poses(motor_traj)

        obj_pos = self.collider.fake_collision(motor_poses)
        raw_sensors = {'object_pos': obj_pos}

        meta['log']['raw_sensors'] = raw_sensors
        return raw_sensors

    def close(self):
        pass

