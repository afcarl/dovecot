from __future__ import division, print_function

import numpy as np

from toolbox import dist
from dynamics.fwdkin import matrices

import sprims

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle


class Roll(sprims.SensoryPrimitive):
    """Highly specific to a situation. Need to be generalized. FIXME"""

    def __init__(self, cfg):
        #self.object_name = cfg.sprimitive.push.object_name
        self.object_name = 'object'
        self.s_feats  = (8, 9)
        self.s_fixed  = (None, 1.0)

    def required_channels(self):
        return (self.object_name + '_ori',)

    def process_context(self, context):
        self.s_bounds = ((-30.0, 30.0), (0.0, 1.0))
        self.real_s_bounds = self.s_bounds

    def process_sensors(self, sensors_data):
        ori_array = sensors_data[self.object_name + '_ori']
        u = np.matrix([[1.0], [0.0], [0.0]])
        angle = 0.0
        last_u = None
        for ori in ori_array:
            ori_rot = matrices.quat2rot(ori)
            x_rot = ori_rot*u
            if last_u is None:
                last_u = x_rot

            dangle = angle_between((last_u[0,0], last_u[1,0], last_u[2,0]),
                                   (x_rot[0,0], x_rot[1,0], x_rot[2,0]))
            angle += dangle
            last_u = x_rot

        return (angle, 0.0 if angle == 0.0 else 1.0)

    @property
    def s_units(self):
        return ('rad', None)

sprims.sprims['roll'] = Roll


class Spin(Roll):
    """Highly specific to a situation. Need to be generalized. FIXME"""

    def __init__(self, cfg):
        #self.object_name = cfg.sprimitive.push.object_name
        Roll.__init__(self, cfg)
        self.s_feats  = (6, 7)
        self.s_fixed  = (None, 1.0)

    def process_context(self, context):
        self.s_bounds = ((-10.0, 10.0), (0.0, 1.0))
        self.real_s_bounds = self.s_bounds

    def process_sensors(self, sensors_data):
        ori_array = sensors_data[self.object_name + '_ori']
        u = np.matrix([[0.0], [0.0], [1.0]])
        angle = 0.0
        last_u = None
        for ori in ori_array:
            ori_rot = matrices.quat2rot(ori)
            x_rot = ori_rot*u
            if last_u is None:
                last_u = x_rot

            dangle = angle_between((last_u[0,0], last_u[1,0], last_u[2,0]),
                                   (x_rot[0,0], x_rot[1,0], x_rot[2,0]))
            angle += dangle
            last_u = x_rot

        return (angle, 0.0 if angle == 0.0 else 1.0)


sprims.sprims['spin'] = Spin

class RollSpin(sprims.SensoryPrimitive):

    def __init__(self, cfg):
        self.spin = Spin(cfg)
        self.roll = Roll(cfg)
        self.s_feats = self.spin.s_feats[:-1]+self.roll.s_feats
        self.s_fixed  = self.spin.s_fixed[:-1]+self.roll.s_fixed


    def process_context(self, context):
        self.roll.process_context(context)
        self.spin.process_context(context)
        self.s_bounds = self.spin.s_bounds[:-1]+self.roll.s_bounds
        self.real_s_bounds = self.s_bounds

    def process_sensors(self, sensors_data):
        effect_spin = self.spin.process_sensors(sensors_data)
        effect_roll = self.roll.process_sensors(sensors_data)
        return effect_spin[:-1]+effect_roll

    @property
    def s_units(self):
        return ('rad', 'rad', None)


sprims.sprims['rollspin'] = RollSpin
