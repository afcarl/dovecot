from __future__ import print_function, division, absolute_import
import math

import numpy as np
import environments

from ..collider import maycollide
from ..collider import collider

from .. import prims
from . import vrepcom


class SimulationEnvironment(environments.PrimitiveEnvironment):

    CollisionError = collider.CollisionError
    MARKER_SIZE = 11

    def __init__(self, cfg):
        super(SimulationEnvironment, self).__init__(cfg)

        self.vrepcom = vrepcom.VRepCom(cfg, verbose=cfg.execute.simu.verbose)

        if cfg.execute.prefilter:
            self._collision_filter = maycollide.CollisionFilter(self.cfg,
                                                                self.vrepcom.caldata.position,
                                                                self.vrepcom.caldata.dimensions,
                                                                self.MARKER_SIZE)

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

    def _check_self_collision(self, ts, motor_poses):
        if self.cfg.execute.check_self_collisions:
            for i, pose in enumerate(motor_poses):
                if i % 3 == 0: # every 30ms.
                    if len(collider.collide(pose)) > 0:
                        if self.cfg.execute.partial_mvt:
                            return i-int(0.5/self.cfg.mprims.dt)
                        else:
                            raise self.CollisionError
        else:
            assert self.cfg.execute.is_simulation

        return len(motor_poses)

    def _trajs2poses(self, trajectories):
        """Transform 6 trajectories in radians in a list of poses in degrees"""
        trajectory = []
        for step in range(self.cfg.mprims.traj_end):
            trajectory.append([math.radians(traj.p(step*self.cfg.mprims.dt)) for traj in trajectories])
        return trajectory

    def _check_object_collision(self, motor_poses):
        if self.cfg.execute.prefilter:
            a = self._collision_filter.may_collide(motor_poses)
            return a
        return True

    def _execute_raw(self, motor_command, meta=None):
        meta['log'] = {}

        motor_poses = self._trajs2poses(motor_command)
        max_index = self._check_self_collision(motor_command[0].ts, motor_poses)
        motor_poses = motor_poses[:max_index]
        if not self._check_object_collision(motor_poses):
            return {}

        raw_sensors = self.vrepcom.run_simulation(motor_poses, self.cfg.mprims.sim_end)
        raw_sensors = self._process_sensors(raw_sensors)

        meta['log']['raw_sensors'] = raw_sensors
        return raw_sensors

    def _process_sensors(self, raw_sensors):
        """Compute processed sensors data"""
        #return {}
        object_sensors = raw_sensors['object_sensors']

        assert len(object_sensors) % (3+4+3+3) == 0
        n = int(len(object_sensors)/13)
        positions    = tuple(tuple(100.0*object_sensors[13*i   :13*i+ 3]) for i in range(n))
        quaternions  = tuple(tuple(      object_sensors[13*i+ 3:13*i+ 7]) for i in range(n))
        # velocities_t = tuple(tuple(object_sensors[13*i+ 7:13*i+10]) for i in range(n))
        # velocities_a = tuple(tuple(object_sensors[13*i+10:13*i+13]) for i in range(n))

        raw_sensors['object_pos']   = positions
        raw_sensors['object_ori']   = quaternions
        # raw_sensors['object_vel_t'] = velocities_t
        # raw_sensors['object_vel_a'] = velocities_a

        if self.cfg.sprims.tip:
            assert raw_sensors['tip_sensors'] is not None
            n = int(len(raw_sensors['tip_sensors'])/3)
            tip_pos = tuple(tuple(raw_sensors['tip_sensors'][3*i:3*i+ 3]) for i in range(n))
            raw_sensors['tip_pos'] = tip_pos

        return raw_sensors

    def close(self):
        self.vrepcom.close(kill=True)
