from __future__ import print_function, division, absolute_import

import numpy as np

from toolbox import dist
import environments

from . import sprims


class Push(environments.SensoryPrimitive):

    def __init__(self, cfg):
        #self.object_name = cfg.sprimitive.push.object_name
        self.object_name = 'object'
        self.s_feats  = (10, 11, 12,)
        self.s_fixed  = (None, None, 1000.0)

    def required_channels(self):
        return (self.object_name + '_pos',)

    def process_context(self, context):
        self.s_channels = [Channel('x', bounds=tuple(context['x_bounds']), unit='mm'),
                           Channel('y', bounds=tuple(context['y_bounds']), unit='mm'),
                           Channel('push_saliency', bounds=(0.0, 1000.0), fixed=1000.0)]

    def process_sensors(self, sensors_data):
        pos_array = sensors_data[self.object_name + '_pos']
        pos_a = pos_array[0]
        pos_b = pos_array[-1]
        collision = 0.0 if dist(pos_a[:2], pos_b[:2]) < 1.0e-2 else 1000.0

        return (pos_b[0]-pos_a[0], pos_b[1]-pos_a[1]) + (collision,)


sprims['push'] = Push
