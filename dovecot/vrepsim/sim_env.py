from __future__ import print_function, division, absolute_import

import copy
import numpy as np
import environments

from ..collider import maycollide
from ..collider import collider

from .. import prims
from . import vrepcom


class SimulationEnvironment(environments.PrimitiveEnvironment):

    MARKER_SIZE = 11

    def __init__(self, cfg):
        super(SimulationEnvironment, self).__init__(cfg)

        self.vrepcom = vrepcom.VRepCom(cfg)

        if cfg.execute.prefilter:
            self._collision_filter = maycollide.CollisionFilter(self.vrepcom.caldata.position,
                                                                self.vrepcom.caldata.dimensions,
                                                                self.MARKER_SIZE)

    def _create_primitives(self, cfg):
        self.context = {'x_bounds': (-300.0, 300.0),
                        'y_bounds': (-300.0, 300.0),
                        'z_bounds': ( 140.0, 330.0)}

        # motor primitive
        self.m_prim = prims.create_mprim(self.cfg.mprim.name, self.cfg)
        self.m_prim.process_context(self.context)

        # sensory primitive
        self.s_prim = environments.ConcatSPrimitive()
        for sprim_name in self.cfg.sprims.names:
            sp = prims.create_sprim(sprim_name, self.cfg)
            sp.process_context(self.context)
            self.s_prim.add_s_prim(sp)

    def _check_self_collision(self, motor_traj):
                # check for self-collisions beforehand
        ts = [self.cfg.mprim.dt/1000.0*i for i in range(len(motor_traj[0]))]

        if self.cfg.execute.check_self_collisions:
            for i, pose in enumerate(motor_traj):
                if i % 3 == 0: # every 50ms.
                    if len(collider.collide(pose)) > 0:
                        if self.cfg.execute.partial_mvt:
                            return ts[:i-10], motor_traj[:i-10]
                        else:
                            return CollisionError
        else:
            assert self.cfg.execute.is_simulation

        return ts, motor_traj

    def _check_object_collision(self, motor_traj):
        if self.cfg.execute.prefilter:
            return not self._collision_filter.may_collide(motor_traj)
        return True

    def _execute_raw(self, motor_command, meta=None):
        motor_traj, max_steps = motor_command

        meta['log'] = {}
        meta['log']['motor_command'] = motor_command

        motor_traj = list(zip(*[np.degrees(t_i[0]) for t_i in motor_traj]))
        ts, motor_traj = self._check_self_collision(motor_traj)
        if not self._check_object_collision(motor_traj):
            return raw_sensors

        raw_sensors = self.vrepcom.run_simulation(motor_traj, max_steps)
        raw_sensors = self._process_sensors(raw_sensors)

        meta['log']['raw_sensors'] = raw_sensors
        return raw_sensors

    def _process_sensors(self, raw_sensors):
        """Compute processed sensors data"""
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
