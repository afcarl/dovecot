"""
Computing motor primitives from high-level orders.
"""

import math
import numpy as np

from . import dmp

def enforce_bounds(data, bounds):
    return tuple(min(bi_max, max(bi_min, d_i)) for di, (bi_min, bi_max) in zip(data, bounds))

mprims = {}

def create_mprim(name, cfg):
    motor_class = mprims[name]
    motor_prim = motor_class(cfg)
    if cfg.mprim.uniformze:
        motor_prim = Uniformize(motor_prim)
    return motor_prim

class MotorPrimitive(object):

    def __init__(self, cfg):
        pass

    def process_context(self, context):
        """Define m_feats and m_bounds here"""
        raise NotImplementedError

    def process_order(self, context):
        """Process order and translate it to simulation-ready motor command"""
        raise NotImplementedError

class Uniformize(MotorPrimitive):

    def __init__(self, motor_prim):
        self.motor_prim = motor_prim

    def process_context(self, context):
        self.motor_prim.process_context(context)
        self.m_feats = self.motor_prim.m_feats
        self.m_bounds = tuple((0.0, 1.0) for i in self.motor_prim.m_bounds)

    def _uni2sim(self, order):
        return tuple(e_i*(b_max - b_min) + b_min for e_i, (b_min, b_max) in zip(order, self.motor_prim.m_bounds))

    def process_order(self, order):
        sim_order = self._uni2sim(order)
        return self.motor_prim.process_order(sim_order)

dmp_limit = 4.0

def dmp2rad(v):
    return 150.0/dmp_limit * (math.pi/180.0) * v

def deg2dmp(v):
    return dmp_limit/150.0*v



class DmpG(MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.size = 6
        self.m_feats = tuple(range(-1, -6*self.size-1, -1))
        self.max_steps     = cfg.mprim.max_steps
        self.n_basis       = cfg.mprim.n_basis
        assert self.n_basis > 1
        self.m_bounds = self.size*self.n_basis*((-400.0, 400.0), (-400.0, 400.0), (0.05, 1.0))
        self.real_m_bounds = self.m_bounds
        self.motor_steps   = cfg.mprim.motor_steps - (cfg.mprim.motor_steps % 2)

        self.dmps = []
        assert len(self.cfg.mprim.init_states) == len(self.cfg.mprim.target_states) == self.size
        for init_state, target_state in zip(self.cfg.mprim.init_states, self.cfg.mprim.target_states):
            d = dmp.DMP()
            d.dmp.set_timesteps(self.motor_steps, 0.0, self.cfg.mprim.end_time)
            d.lwr_meta_params(self.n_basis)
            d.dmp.set_initial_state([deg2dmp(init_state)])
            d.dmp.set_attractor_state([deg2dmp(target_state)])

            self.dmps.append(d)

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
            ys = dmp2rad(np.array(ys))
            #print('{}: {:6.2f}/{:6.2f}'.format(i, 180.0/math.pi*np.min(ys), 180.0/math.pi*np.max(ys)))

            traj.append((tuple(ys), self.cfg.mprim.max_speed))

        return tuple(traj), self.max_steps

mprims['dmpg'] = DmpG

class Dmp1G(MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.size = 6
        self.m_feats = tuple(range(-1, -4*self.size-1, -1))
        self.m_bounds = self.size*((-400.0, 400.0), (-400.0, 400.0),
                                   (0.0, 1.0), (0.05, 1.0))
        self.real_m_bounds = self.m_bounds
        self.motor_steps = cfg.mprim.motor_steps - (cfg.mprim.motor_steps % 2)
        self.max_steps   = cfg.mprim.max_steps
        self.n_basis       = cfg.mprim.n_basis
        assert self.n_basis == 1

        self.dmps = []
        assert len(self.cfg.mprim.init_states) == len(self.cfg.mprim.target_states) == self.size
        for init_state, target_state in zip(self.cfg.mprim.init_states, self.cfg.mprim.target_states):
            d = dmp.DMP()
            d.dmp.set_timesteps(int(self.motor_steps/2), 0.0, 1.25)
            d.lwr_meta_params(1)
            d.dmp.set_initial_state([deg2dmp(init_state)])
            d.dmp.set_attractor_state([deg2dmp(target_state)])

            self.dmps.append(d)

    def process_context(self, context):
        pass

    def process_order(self, order):
        assert len(order) == 4*self.size

        traj = []
        for i, d in enumerate(self.dmps):
            slope, offset, center, width = order[4*i:4*i+4]
            d.lwr_model_params([center], [width], [slope], [offset])
            ts, ys, yds = d.trajectory()
            ys = 150.0/8.0 * (math.pi/180.0) * np.array(ys)
            #print('{}: {:6.2f}/{:6.2f}'.format(i, 180.0/math.pi*np.min(ys), 180.0/math.pi*np.max(ys)))
            yds = [self.cfg.mprim.max_speed]*len(ys)
            traj.append((tuple(ys), tuple(yds)))

        #print('')

        return tuple(traj), self.max_steps

mprims['dmp1g'] = Dmp1G
