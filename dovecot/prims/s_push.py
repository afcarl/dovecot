from __future__ import print_function, division, absolute_import
import random

import numpy as np

from ..ext.toolbox import dist

from environments import Channel
import environments

from environments import tools
from . import sprims


class Push(environments.SensoryPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.tracked_objects = []
        for obj_name, obj_cfg in cfg.execute.scene.objects._children_items():
            if obj_cfg.tracked:
                self.tracked_objects.append(obj_name)

        assert len(self.tracked_objects) == 1
        self.object_name = self.tracked_objects[0]

    def required_channels(self):
        return (self.object_name + '.pos',)

    def process_context(self, context):
        self.s_channels = [Channel('x', bounds=tuple(context['x_bounds']), unit='mm'),
                           Channel('y', bounds=tuple(context['y_bounds']), unit='mm'),
                           Channel('push_saliency', bounds=(0.0, 1000.0), fixed=1000.0)]
        self._s_channels = self.s_channels
        objects = context['objects']
        obj_cal = objects[self.object_name]
        obj_pos = obj_cal.actual_pos(obj_cal.pos_w, self.cfg.execute.scene.objects[self.object_name].pos)

        self.null_effect = (obj_pos[0], obj_pos[1], 0.0)

    def process_raw_sensors(self, sensors_data):
        if self.cfg.sprims.max_force > 0:
            for contact in sensors_data.get('contacts', []):
                if contact.force_norm_sq > self.cfg.sprims.max_force:
                    return tools.to_signal(self.null_effect, self._s_channels)
        if self.object_name + '.pos' not in sensors_data:
            return tools.to_signal(self.null_effect, self._s_channels) # does this hide bugs ? when is it necessary ?

        pos_array = sensors_data[self.object_name + '.pos']
        pos_a = pos_array[0]
        pos_b = pos_array[-1]
        collision = 0.0 if dist(pos_a[:2], pos_b[:2]) < 1.0 else 1000.0

        return tools.to_signal((pos_b[0], pos_b[1]) + (collision,), self._s_channels)
#        return tools.to_signal((pos_b[0]-pos_a[0], pos_b[1]-pos_a[1]) + (collision,), self._s_channels)

class PushCollision(Push):

    def process_context(self, context):
        super(PushCollision, self).process_context(context)
        self.s_channels = [Channel('c', bounds=(0.0, 1.0))]

    def process_raw_sensors(self, sensors_data):
        s_signal = super(PushCollision, self).process_raw_sensors(sensors_data)
        if s_signal['push_saliency'] == 0:
            return {'c': random.uniform(0.0, 0.5)}
        else:
            return {'c': random.uniform(0.5, 1.0)}


sprims['push'] = Push
sprims['push_collision'] = PushCollision
