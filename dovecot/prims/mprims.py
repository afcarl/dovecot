"""
Computing motor primitives from high-level orders.
"""
from __future__ import print_function, division, absolute_import
import math

import numpy as np

from . import dmp

import environments
from environments import Channel


mprims = {}

def create_mprim(name, cfg):
    motor_class = mprims[name]
    motor_prim = motor_class(cfg)
    return motor_prim

dmp_limit = 4.0

def dmp2rad(v):
    return 150.0/dmp_limit * (math.pi/180.0) * v

def deg2dmp(v):
    return dmp_limit/150.0*v


class DmpG25(environments.MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.size = 6
        self.n_basis   = cfg.mprim.n_basis
        self.max_steps = cfg.mprim.max_steps

        self.motor_steps   = cfg.mprim.motor_steps - (cfg.mprim.motor_steps % 2)
        self.dmps = []
        assert len(self.cfg.mprim.init_states) == len(self.cfg.mprim.target_states) == self.size
        for init_state, target_state in zip(self.cfg.mprim.init_states, self.cfg.mprim.target_states):
            d = dmp.DMP(self.cfg.mprim.dt)
            d.dmp.set_timesteps(self.motor_steps, 0.0, self.cfg.mprim.end_time)
            d.lwr_meta_params(self.n_basis)
            d.dmp.set_initial_state([deg2dmp(init_state)])
            d.dmp.set_attractor_state([deg2dmp(target_state)])

            self.dmps.append(d)

        self.m_channels = []
        for motor in range(self.size):
            for i in range(self.n_basis):
                self.m_channels += [Channel('slope{}.{}'.format(motor, i), (-400, 400)),
                                    Channel('offset{}.{}'.format(motor, i), (-400, 400))]
        for i in range(self.n_basis):
            self.m_channels += [Channel('width{}'.format(i), (0.05, 1.0))]


    def process_context(self, context):
        pass

    def process_motor_signal(self, order):
        assert len(order) == self.n_basis*(2*self.size+1)

        traj = []

        widths = order[-self.n_basis:]
        centers = tuple(np.linspace(0.0, 1.0, num=self.n_basis+2)[1:-1])

        for i, d in enumerate(self.dmps):
            slopes, offsets = [], []
            for j in range(self.n_basis):
                cursor = 2 * (self.n_basis * i + j)
                slope, offset = order[cursor:cursor + 2]
                slopes.append(slope)
                offsets.append(offset)

            d.lwr_model_params(centers, widths, slopes, offsets)
            ts, ys, yds = d.trajectory()
            ys = self.dmp2angle_rad(i, np.array(ys))

            traj.append((tuple(ys), self.cfg.mprim.max_speed))

        return tuple(traj), self.max_steps

    def dmp2angle_rad(self, i, ys):
        """In radians"""
        assert self.cfg.mprim.angle_ranges[i][0] == self.cfg.mprim.angle_ranges[i][1], "angles range of {}th motor are not symmetric: {}".format(i, self.cfg.mprim.angle_ranges[i])
        r = self.cfg.mprim.angle_ranges[i][1]
        return r/5.0 * (math.pi/180.0) * ys

    def deg_angle2dmp(self, i, a):
        """In radians"""
        assert self.cfg.mprim.angle_ranges[i][0] == self.cfg.mprim.angle_ranges[i][1]
        r = self.cfg.mprim.angle_ranges[i][1]
        return 5.0/r * (180/math.pi) * a


mprims['dmpg25'] = DmpG25

class DmpG(DmpG25):

    def __init__(self, cfg):
        super(DmpG, self).__init__(cfg)

        self.m_channels = []
        for motor in range(self.size):
            for i in range(self.n_basis):
                self.m_channels += [Channel('slope{}.{}'.format(motor, i), (-400, 400)),
                                    Channel('offset{}.{}'.format(motor, i), (-400, 400)),
                                    Channel('width{}.{}'.format(motor, i), (0.05, 1.0))]

    def process_context(self, context):
        pass

    def process_order(self, order):
        assert len(order) == 3*self.n_basis*self.size

        traj = []
        centers = tuple(np.linspace(0.0, 1.0, num=self.n_basis+2)[1:-1])

        for i, d in enumerate(self.dmps):
            slopes, offsets, widths = [], [], []
            for j in range(self.n_basis):
                cursor = 3 * (self.n_basis * i + j)
                slope, offset, width = order[cursor:cursor + 3]
                slopes.append(slope)
                offsets.append(offset)
                widths.append(width)

            d.lwr_model_params(centers, widths, slopes, offsets)
            ts, ys, yds = d.trajectory()

            ys = self.dmp2angle_rad(i, np.array(ys))

            traj.append((tuple(ys), self.cfg.mprim.max_speed))

        return tuple(traj), self.max_steps


mprims['dmpg'] = DmpG
