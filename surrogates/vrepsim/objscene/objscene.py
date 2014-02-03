"""
    Scene for object execution.
"""
import os

scenes = {}

class ObjectScene(object):

    def __init__(self, name, filename,
                       object_pos=None,
                       object_geoms=None):
        self.name = name
        assert self.name not in scenes
        scenes[self.name] = self
        self.filename = os.path.expanduser(os.path.join(os.path.dirname(__file__), filename))
        assert os.path.isfile(self.filename), "file {} not found".format(self.filename)
        self.object_pos = object_pos
        self.object_geoms = object_geoms

ObjectScene(name='cube',
            filename='ar.ttt',
            object_pos=  (12.474, 12.095, 15.574),
            object_geoms=(  45.0,  45.0,   45.0))
ObjectScene(name='cube_center',
            filename='ar_center.ttt',
            object_pos=  (24.544, 0.050, 15.574),
            object_geoms=(  45.0,  45.0,   45.0))

