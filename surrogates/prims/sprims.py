"""
Computing sensory primitives from raw data.
"""
from __future__ import division

import math

sprims = {}

def create_sprim(name, cfg):
    sensory_class = sprims[name]
    sensory_prim = sensory_class(cfg)
    if cfg.sprims.uniformize:
        sensory_prim = Uniformize(sensory_prim)
    return sensory_prim

class SensoryPrimitive(object):

    def __init__(self, cfg):
        pass

    def required_channels(self):
        """Defines used channels for this sensory primitive"""
        raise NotImplementedError

    def process_context(self, context):
        """Define s_feats, s_bounds and s_fixed here"""
        raise NotImplementedError

    def process_sensors(self, context):
        """Process sensory data and return effect"""
        raise NotImplementedError

    def units(self):
        """Return a list the physical units for each dimension"""
        raise NotImplementedError
        

def enforce_bounds(data, bounds):
    return tuple(min(bi_max, max(bi_min, d_i)) for di, (bi_min, bi_max) in zip(data, bounds))

def isobarycenter(bounds):
    return tuple((b+a)/2.0 for a, b in bounds)

class Uniformize(SensoryPrimitive):

    def __init__(self, sensory_prim):
        self.sensory_prim = sensory_prim

    def required_channels(self):
        return self.sensory_prim.required_channels()

    def process_context(self, context):
        self.sensory_prim.process_context(context)
        self.s_feats  = self.sensory_prim.s_feats
        self.s_bounds = tuple((0.0, 1.0) for _ in self.sensory_prim.s_bounds)
        self.real_s_bounds = self.sensory_prim.s_bounds
        self.s_fixed  = self.sensory_prim.s_fixed # FIXME uniformize

    def _sim2uni(self, effect):
        assert len(effect) == len(self.s_feats)
        return tuple((e_i - s_min)/(s_max - s_min) for e_i, (s_min, s_max) in zip(effect, self.sensory_prim.s_bounds))

    def process_sensors(self, sensors_data):
        effect = self.sensory_prim.process_sensors(sensors_data)
        return self._sim2uni(effect)

    def units(self):
        return self.sensory_prim.units()

# class Push(SensoryPrimitive):

#     def __init__(self, cfg):
#         self.object_name = 'object'

#     def required_channels(self):
#         return (self.object_name + '_pos',)

#     def process_context(self, context):
#         self.s_feats = (0, 1, 2,)
#         self.s_bounds = (context['x_bounds'],) + (context['y_bounds'],) + ((0.0, 1.0),)
#         self.real_s_bounds = self.s_bounds
#         self.s_fixed = (None, None, 1.0)

#     def process_sensors(self, sensors_data):
#         pos_array = sensors_data['object_pos']
#         pos_a = pos_array[0]
#         pos_b = pos_array[-1]
#         collision = 0.0 if pos_a == pos_b else 1.0

#         return tuple(pos_b) + (collision,)

#     @property
#     def s_units(self):
#         return ('mm', 'mm', None)

# sprims['push'] = Push

