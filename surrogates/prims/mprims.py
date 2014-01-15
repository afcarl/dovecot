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


class Dmp1G(MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.size = 6
        self.m_feats = tuple(range(-1, -4*self.size-1, -1))
        self.m_bounds = self.size*((-400.0, 400.0), (-400.0, 400.0),
                                   (0.0, 1.0), (0.0, 1.0))
        self.real_m_bounds = self.m_bounds
        self.motor_steps = cfg.mprim.motor_steps - (cfg.mprim.motor_steps % 2) 
        self.max_steps   = cfg.mprim.max_steps

        self.dmps = []
        for j in range(self.size):
            d = dmp.DMP()
            d.dmp.set_timesteps(int(self.motor_steps/2), 0.0, 2.0)
            d.lwr_meta_params(1)
            d.dmp.set_initial_state([0.0])
            d.dmp.set_attractor_state([0.0])

            self.dmps.append(d)

    def process_context(self, context):
        pass

    def process_order(self, order):
        assert len(order) == 4*self.size

        traj = []
        for i, d in enumerate(self.dmps):
            slope, offset, center, width = order[4*i:4*i+4]
            d.lwr_model_params([center], [width], [slope], [offset])
            #d.lwr_model_params([center], [width], [slope], [offset])
            #d.lwr_model_params([center], [width], [slope], [offset])
            ts, ys, yds = d.trajectory()
            print(np.array(ys))
            ys = 150.0/8.0 * (math.pi/180.0) * np.array(ys) 
            print(ys)
            # yds = np.absolute(yds)
            # yds = math.pi/25.0 * np.array(yds)
            yds = [0.25]*len(ys)
            traj.append((tuple(ys), tuple(yds)))

        return tuple(traj), self.max_steps

mprims['dmp1g'] = Dmp1G
