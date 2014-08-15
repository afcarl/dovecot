from __future__ import print_function, division, absolute_import
import math

import numpy as np

import environments

from ..vrepsim import sim_env
from ..collider import maycollide
from .. import prims
from .. import ttts


class KinEnvironment(sim_env.SimulationEnvironment):

    def __init__(self, cfg):
        self.cfg = cfg
        self.caldata = ttts.TTTCalibrationData(self.cfg.execute.scene.name, self.cfg.execute.simu.calibrdir)
        self.caldata.load()

        environments.PrimitiveEnvironment.__init__(self, cfg)

        self.tracked_objects = []
        for obj_name, obj_cfg in cfg.execute.scene.objects._children_items():
            if obj_cfg.tracked:
                self.tracked_objects.append(obj_name)
        assert len(self.tracked_objects) == 1

        self.obj_name = self.tracked_objects[0]
        obj = self.caldata.objects[self.obj_name]
        obj_pos_w = obj.actual_pos(obj.pos_w, self.cfg.execute.scene.objects[self.obj_name].pos)
        obj_pos   = tuple(np.array(obj.pos) + np.array(obj_pos_w) - np.array(obj.pos_w))
        print(obj_pos)

        self.collider = maycollide.FakeColliderCube(self.cfg, obj_pos,
                                                    obj.dim, self.MARKER_SIZE)

    def _execute_raw(self, motor_command, meta=None):

        motor_traj = motor_command

        meta['log'] = {}

        motor_poses = self._trajs2poses(motor_traj)

        obj_pos = self.collider.fake_collision(motor_poses)
        raw_sensors = {'{}.pos'.format(self.obj_name): obj_pos}

        meta['log']['raw_sensors'] = raw_sensors
        return raw_sensors

    def close(self):
        pass

