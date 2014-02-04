"""
    Scene for object execution.
"""
import os

scenes = {}

class ObjectScene(object):

    def __init__(self, name, filename,
                       object_pos=None,
                       object_geom=None):
        self.name = name
        assert self.name not in scenes
        scenes[self.name] = self
        self.filename = os.path.expanduser(os.path.join(os.path.dirname(__file__), filename))
        assert os.path.isfile(self.filename), "file {} not found".format(self.filename)
        self.object_pos = object_pos
        self.object_geom = object_geom

ObjectScene(name='cube',
            filename='ar.ttt',
            object_pos=  (124.74, 120.95, 155.74),
            object_geom=(  45.0/2,  45.0/2,   45.0/2))
ObjectScene(name='cube_center',
            filename='ar_center.ttt',
            object_pos=  (195.44, 0.50, 155.74),
            object_geom=(  45.0/2,  45.0/2,   45.0/2))

