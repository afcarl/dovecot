from __future__ import print_function, division, absolute_import
import math

import numpy as np
import environments

from ..collider import maycollide
from ..collider import collider

from .. import prims
from . import vrepcom

# NOT DRY
x, y, z = 0.0, 0.0, 0.0
contexts = {'arena6x6x4':    {'x_bounds': ( -300.0 + x,  300.0 + x),
                              'y_bounds': ( -300.0 + y,  300.0 + y),
                              'z_bounds': (    0.0 + z,  400.0 + z)},
            'arena10x10x4':  {'x_bounds': ( -500.0 + x,  500.0 + x),
                              'y_bounds': ( -500.0 + y,  500.0 + y),
                              'z_bounds': (    0.0 + z,  400.0 + z)},
            'arena20x20x10': {'x_bounds': (-1000.0 + x, 1000.0 + x),
                              'y_bounds': (-1000.0 + y, 1000.0 + y),
                              'z_bounds': (    0.0 + z, 1000.0 + z)},
           }

class SimulationEnvironment(environments.PrimitiveEnvironment):

    CollisionError = collider.CollisionError
    MARKER_SIZE = 11
    com_class = vrepcom.VRepCom

    def __init__(self, cfg):
        self.vrepcom = self.com_class(cfg, verbose=cfg.execute.simu.verbose)
        self.caldata = self.vrepcom.caldata

        super(SimulationEnvironment, self).__init__(cfg)
        self._info = self.vrepcom.get_info()

        if cfg.execute.prefilter:
            tracked_objects = []
            for obj_name, obj_cfg in self.cfg.execute.scene.objects._children_items():
                if obj_cfg.tracked:
                    tracked_objects.append(obj_name)
            assert len(tracked_objects) == 1

            obj_name = tracked_objects[0]
            obj = self.caldata.objects[obj_name]
            obj_pos_w = obj.actual_pos(obj.pos_w, self.cfg.execute.scene.objects[obj_name].pos)

            self._collision_filter = maycollide.CollisionFilter(self.cfg,
                                                                self.caldata.pos_r(obj_pos_w),
                                                                obj.dim,
                                                                self.MARKER_SIZE)

    def _create_primitives(self, cfg):
        self.context = {'objects': self.caldata.objects}
        self.context.update(contexts[self.cfg.execute.scene.arena.name]) # HACK
        if hasattr(self, 'vrepcom'):
            self.context.update(self.vrepcom.context)

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
                    if len(collider.collide([math.degrees(p) for p in pose])) > 0:
                        if self.cfg.execute.partial_mvt:
                            return i-int(0.1/self.cfg.mprims.dt)
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
            return self._collision_filter.may_collide(motor_poses)
        return True

    def _execute_raw(self, motor_command, meta=None):
        meta['log'] = {}

        motor_poses = self._trajs2poses(motor_command)
        max_index = self._check_self_collision(motor_command[0].ts, motor_poses)
        motor_poses = motor_poses[:max_index]
        if not self._check_object_collision(motor_poses):
            return {'flag': 'no_collision'}

        raw_sensors = self.vrepcom.run_simulation(motor_poses)
        raw_sensors = self._process_sensors(raw_sensors)

        meta['log']['raw_sensors'] = raw_sensors
        return raw_sensors

    def _process_sensors(self, raw_sensors):
        """Compute processed sensors data"""
        object_sensors = raw_sensors['object_sensors']
        import sys
        # print('traked_objects: {}'.format(self.vrepcom.tracked_objects), file=sys.stderr)
        # print('object_sensors: {}'.format(object_sensors), file=sys.stderr)

        assert len(object_sensors) % (3+4+3+3) == 0
        n_objs = len(self.vrepcom.tracked_objects)
        for k, obj_name in enumerate(self.vrepcom.tracked_objects):
            n = int(len(object_sensors)/(13*n_objs))
            positions    = tuple(tuple(100.0*object_sensors[13*(n_objs*i+k)   :13*(n_objs*i+k)+ 3]) for i in range(n))
            quaternions  = tuple(tuple(      object_sensors[13*(n_objs*i+k)+ 3:13*(n_objs*i+k)+ 7]) for i in range(n))
            # velocities_t = tuple(tuple(object_sensors[13*i+ 7:13*i+10]) for i in range(n))
            # velocities_a = tuple(tuple(object_sensors[13*i+10:13*i+13]) for i in range(n))

            raw_sensors['{}.pos'.format(obj_name)]   = positions
            raw_sensors['{}.ori'.format(obj_name)]   = quaternions
            # raw_sensors['object_vel_t'] = velocities_t
            # raw_sensors['object_vel_a'] = velocities_a

        if self.cfg.sprims.tip:
            assert raw_sensors['marker_sensors'] is not None
            n = int(len(raw_sensors['marker_sensors'])/3)
            tip_pos = tuple(tuple(raw_sensors['marker_sensors'][3*i:3*i+ 3]) for i in range(n))
            raw_sensors['tip_pos'] = tip_pos

        return raw_sensors

    def close(self, kill=True):
        self.vrepcom.close(kill=kill)
