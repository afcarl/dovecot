from __future__ import print_function, division, absolute_import

import numpy as np

from toolbox import dist
from dynamics.fwdkin import matrices
from environments import Channel
from environments import tools

from . import sprims
from . import s_push


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



class Roll(s_push.Push):
    """Highly specific to a situation. Need to be generalized. FIXME"""

    def required_channels(self):
        return (self.object_name + '.ori',)

    def process_context(self, context):
        self.s_channels = [Channel('roll', bounds=(-30.0, 30.0), unit='rad'),
                           Channel('roll_saliency', bounds=(0.0, 1.0), fixed=1.0)]

    def process_raw_sensors(self, sensors_data):
        ori_array = sensors_data[self.object_name + '.ori']
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

        return tools.to_signal((angle, 0.0 if angle < 1e-2 else 50.0), self.s_channels)


sprims['roll'] = Roll


class Spin(Roll):
    """Highly specific to a situation. Need to be generalized. FIXME"""

    def process_context(self, context):
        self.s_channels = [Channel('spin', bounds=(-10.0, 10.0), unit='rad'),
                           Channel('spin_saliency', bounds=(0.0, 1.0), fixed=1.0)]

    def process_raw_sensors(self, sensors_data):
        ori_array = sensors_data[self.object_name + '.ori']
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

        return tools.to_signal((angle, 0.0 if angle < 1e-2 else 50.0), self.s_channels)


sprims['spin'] = Spin


class RollSpin(Roll):

    def __init__(self, cfg):
        self.spin = Spin(cfg)
        self.roll = Roll(cfg)

    def process_context(self, context):
        self.roll.process_context(context)
        self.spin.process_context(context)
        self.s_channels = [self.roll.s_channels[0], self.spin.s_channels[0],
                           Channel('rollspin_saliency', bounds=(0, 50), fixed=50)]

    def process_raw_sensors(self, sensors_data):
        effect_spin = tools.to_vector(self.spin.process_raw_sensors(sensors_data), self.spin.s_channels)
        effect_roll = tools.to_vector(self.roll.process_raw_sensors(sensors_data), self.roll.s_channels)
        if effect_spin[-1] == effect_roll[-1] == 0.0:
            effect = effect_spin[:-1] + effect_roll[:-1] + (0.0,)
        else:
            effect = effect_spin[:-1] + effect_roll[:-1] + (50.0,)

        return tools.to_signal(effect, self.s_channels)


sprims['rollspin'] = RollSpin
