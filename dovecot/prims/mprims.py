"""
Computing motor primitives from high-level orders.
"""
from __future__ import print_function, division, absolute_import
import math
import bisect

import numpy as np

from . import dmp

import environments
from environments import Channel
from environments import tools

mprims = {}

def create_mprim(name, cfg):
    motor_class = mprims[name]
    motor_prim = motor_class(cfg)
    return motor_prim


def deg2dmp(v):
    return 5.0/150.0*v

class Trajectory(object):

    def __init__(self, ts, ps, max_speed=None):
        """
        :param ts:  is a list of time
        :param ps:  is a list of points (or scalar)
        """
        assert len(ts) == len(ps)
        self.ts = ts
        self.ps = ps
        self.max_speed = max_speed

    def p(self, t):
        idx = min(len(self.ps)-1, bisect.bisect_right(self.ts, t))
        return self.ps[idx]

    def truncate(self, index):
        self.ts = self.ts[:index]
        self.ps = self.ps[:index]

    @property
    def max_t(self):
        return self.ts[-1]

    def __len__(self):
        return len(self.ts)


class DmpSharedWidth(environments.MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.size     = len(self.cfg.mprims.init_states)
        self.n_basis  = self.cfg.mprims.n_basis
        self.sim_end  = self.cfg.mprims.sim_end
        self.traj_end = self.cfg.mprims.traj_end - (cfg.mprims.traj_end % 2)
        assert len(self.cfg.mprims.init_states) == len(self.cfg.mprims.target_states) == self.size

        self.dmps = []
        for i, (init_state, target_state) in enumerate(zip(self.cfg.mprims.init_states, self.cfg.mprims.target_states)):
            d = dmp.DMP(self.cfg.mprims.dt)
            total_time = self.traj_end/self.cfg.mprims.target_end
            d.dmp.set_timesteps(self.traj_end, 0.0, total_time)
            d.lwr_meta_params(self.n_basis)
            d.dmp.set_initial_state([self.deg_angle2dmp(i, init_state)])
            d.dmp.set_attractor_state([self.deg_angle2dmp(i, target_state)])

            self.dmps.append(d)

        self.m_channels = []
        for motor in range(self.size):
            for i in range(self.n_basis):
                self.m_channels += [Channel('slope{}.{}'.format(motor, i), (-400, 400)),
                                    Channel('offset{}.{}'.format(motor, i), (-400, 400))]
        for i in range(self.n_basis):
            self.m_channels += [Channel('width{}'.format(i), (0.05/self.n_basis, 1.0/self.n_basis))]


    def process_context(self, context):
        pass

    def process_motor_signal(self, m_signal):
        assert len(m_signal) == self.n_basis*(2*self.size+1)

        traj = []
        m_vector = tools.to_vector(m_signal, self.m_channels)

        widths = m_vector[-self.n_basis:]
        centers = tuple(np.linspace(0.0, 1.0, num=self.n_basis+2)[1:-1])

        for i, d in enumerate(self.dmps):
            slopes, offsets = [], []
            for j in range(self.n_basis):
                cursor = 2 * (self.n_basis * i + j)
                slope, offset = m_vector[cursor:cursor + 2]
                slopes.append(slope)
                offsets.append(offset)

            d.lwr_model_params(centers, widths, slopes, offsets)
            ts, ys, yds = d.trajectory()
            ts = self.cfg.mprims.target_end*self.cfg.mprims.dt*np.array(ts)
            ys = self.dmp2angle_deg(i, np.array(ys))

            traj_i = Trajectory(ts, ys, self.cfg.mprims.max_speed)
            traj.append(traj_i)

        return traj

    def dmp2angle_deg(self, i, ys):
        """In radians"""
        assert self.cfg.mprims.angle_ranges[i][0] == self.cfg.mprims.angle_ranges[i][1], "angles range of {}th motor are not symmetric: {}".format(i, self.cfg.mprims.angle_ranges[i])
        r = self.cfg.mprims.angle_ranges[i][1]
        return r/5.0 * ys

    def deg_angle2dmp(self, i, a):
        """In radians"""
        assert self.cfg.mprims.angle_ranges[i][0] == self.cfg.mprims.angle_ranges[i][1]
        r = self.cfg.mprims.angle_ranges[i][1]
        return 5.0/r * a

mprims['dmp_sharedwidth'] = DmpSharedWidth
