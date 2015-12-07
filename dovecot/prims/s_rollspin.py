from __future__ import print_function, division, absolute_import
import sys

import numpy as np

from environments import Channel
from environments import tools

from ..ext.toolbox import dist
from ..ext.dynamics.fwdkin import matrices
from . import sprims
from . import s_push


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'    """
    cosang = np.dot(v1, v2)
    sinang = np.linalg.norm(np.cross(v1, v2))
    return np.arctan2(sinang, cosang)



class Roll(s_push.Push):
    """Highly specific to a situation. Need to be generalized. FIXME"""

    def required_channels(self):
        return (self.object_name + '.ori',)

    def process_context(self, context):
        self.s_channels = [Channel('roll', bounds=(-40.0, 40.0), unit='rad'),
                           Channel('roll_saliency', bounds=(0.0, 1000.0), fixed=1000.0)]

    def process_raw_sensors(self, sensors_data):
        try:
            ori_array = sensors_data[self.object_name + '.ori']
        except KeyError:
            assert sensors_data['flag'] == 'no_collision'
            return tools.to_signal((0.0, 0.0), self.s_channels)
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

        return tools.to_signal((angle, 0.0 if angle < 1e-2 else 1000.0), self.s_channels)


sprims['roll'] = Roll


class Spin(Roll):
    """Highly specific to a situation. Need to be generalized. FIXME"""

    def process_context(self, context):
        self.s_channels = [Channel('spin', bounds=(-40.0, 40.0), unit='rad'),
                           Channel('spin_saliency', bounds=(0.0, 1.0), fixed=1000.0)]

    def process_raw_sensors(self, sensors_data):

        # print('sensors_data_keys: {}'.format(sensors_data.keys()), file=sys.stderr)
        try:
            ori_array = sensors_data[self.object_name + '.ori']
        except KeyError:
            assert sensors_data['flag'] == 'no_collision'
            return tools.to_signal((0.0, 0.0), self.s_channels)
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
            #print('spin\n{}\n{}\n{}\n{}'.format(last_u.T, x_rot.T, (last_u-x_rot).T, dangle))
            angle += dangle
            last_u = x_rot

        return tools.to_signal((angle, 0.0 if angle < 1e-2 else 1000.0), self.s_channels)


sprims['spin'] = Spin


class RollSpin(Roll):

    def __init__(self, cfg):
        self.spin = Spin(cfg)
        self.roll = Roll(cfg)

    def process_context(self, context):
        self.roll.process_context(context)
        self.spin.process_context(context)
        self.s_channels = [self.roll.s_channels[0], self.spin.s_channels[0],
                           Channel('rollspin_saliency', bounds=(0, 1000), fixed=1000.0)]

    def process_raw_sensors(self, sensors_data):
        effect_spin = tools.to_vector(self.spin.process_raw_sensors(sensors_data), self.spin.s_channels)
        effect_roll = tools.to_vector(self.roll.process_raw_sensors(sensors_data), self.roll.s_channels)
        if effect_spin[-1] == effect_roll[-1] == 0.0:
            effect = effect_spin[:-1] + effect_roll[:-1] + (0.0,)
        else:
            effect = effect_spin[:-1] + effect_roll[:-1] + (1000.0,)

        return tools.to_signal(effect, self.s_channels)


sprims['rollspin'] = RollSpin
