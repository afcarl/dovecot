import sprims

class Push(sprims.SensoryPrimitive):

    def __init__(self, cfg):
        #self.object_name = cfg.sprimitive.push.object_name
        self.object_name = 'object'        
        self.s_feats  = (10, 11, 12,)
        self.s_fixed  = (None, None, 1.0)

    def required_channels(self):
        return (,)

    def process_context(self, context):
        self.s_bounds = tuple(context['x_bounds']) + tuple(context['y_bounds']) + ((0.0, 1.0),)

    def process_sensors(self, sensors_data):
        pos_array = sensors_data[self.object_name + '_pos']
        pos_a = pos_array[0]
        pos_b = pos_array[-1]
        collision = 0.0 if pos_a == pos_b else 1.0

        return tuple(pos_b) + (collision,)

    def units(self):
        return ('m', 'm', None)

sprims['push'] = Push
