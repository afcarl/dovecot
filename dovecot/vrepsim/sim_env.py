from __future__ import print_function, division, absolute_import

import numpy as np
import environments

from ..collider import maycollide
from ..logger import logger

from .. import prims
from . import vrepcom


class SimulationEnvironment(environment.PrimitiveEnvironment):

    MARKER_SIZE = 11

    def __init__(self, cfg):
        super(SimulationEnvironment, self).__init__(cfg)

        self.vrepcom = vrepcom.VRepCom(cfg)

        if cfg.sprims.prefilter:
            self._collision_filter = maycollide.CollisionFilter(self.vrepcom.caldata.position,
                                                                self.vrepcom.caldata.dimensions,
                                                                self.MARKER_SIZE)

        self.use_logger = self.cfg.logger.enabled
        if self.use_logger:
            self.logger = logger.Logger(filename   =self.cfg.logger.filename,
                                        folder     =self.cfg.logger.folder,
                                        write_delay=self.cfg.logger.write_delay,
                                        ignored    =self.cfg.logger.ignored)
            self.logger.start()

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
        motor_traj = list(zip(*[np.degrees(t_i[0]) for t_i in motor_traj]))
                # check for self-collisions beforehand
        ts = [self.mprim.dt/1000.0*i for i in range(len(motor_traj[0][0]))]

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
        if self.cfg.sprims.prefilter:
            motor_traj_2 = list(zip(*[np.degrees(t_i[0]) for t_i in motor_traj]))
            return not self._collision_filter.may_collide(motor_traj_2):
        return True

    def _execute_raw(self, motor_command, meta=None):
        motor_traj, max_steps = motor_command

        raw_sensors = {'motor_traj': motor_traj}

        ts, motor_traj = self._check_self_collision(motor_traj)
        if not self._check_object_collision(motor_traj):
            return raw_sensors

        raw_sensors = self.vrepcom.run_simulation(motor_traj, max_steps, t=t)
        raw_sensors = self._process_sensors(raw_sensors)

        if self.use_logger:
            data_log = copy.deepcopy(raw_sensors)
            data_log['order'] = m_vector
            data_log['scene'] = 'vrep_{}'.format(self.cfg.sprims.scene)
            self.logger.log(data_log, step=t)

        return raw_sensors

    def _process_sensors(self, raw_sensors):
        """Compute processed sensors data"""

        assert len(object_sensors) % (3+4) == 0
        n = int(len(object_sensors)/7)
        positions    = tuple(tuple(100.0*object_sensors[7*i   :7*i+ 3]) for i in range(n))
        quaternions  = tuple(tuple(      object_sensors[7*i+ 3:7*i+ 7]) for i in range(n))
        # velocities_t = tuple(tuple(object_sensors[13*i+ 7:13*i+10]) for i in range(n))
        # velocities_a = tuple(tuple(object_sensors[13*i+10:13*i+13]) for i in range(n))

        raw_sensors['object_pos']   = positions
        raw_sensors['object_ori']   = quaternions
        # raw_sensors['object_vel_t'] = velocities_t
        # raw_sensors['object_vel_a'] = velocities_a

        if self.cfg.sprims.tip:
            assert tip_sensors is not None
            n = int(len(tip_sensors)/3)
            tip_pos = tuple(tuple(tip_sensors[3*i:3*i+ 3]) for i in range(n))
            raw_sensors['tip_pos'] = tip_pos

        return raw_sensors

    def close(self):
        self.vrepcom.close(kill=True)
