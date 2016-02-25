import sympy
import numpy as np

from . import matrices

def homogeneous2quaternions(T):
    assert T.shape == (4, 4)


class FclBody(object):

    def update(self, angles, T):
        self.T = T

    @property
    def quat(self):
        return matrices.hm2quat(self.T)

    @property
    def rot(self):
        return matrices.hm2rot(self.T)

    @property
    def trans(self):
        return matrices.hm2trans(self.T)

    @property
    def geom(self):
        raise NotImplementedError

    def bodies(self):
        return [self]

class Box(FclBody):

    def __init__(self, size, meta=None, groups=()):
        assert len(size) == 3
        self.size = tuple(size)
        self.meta = meta
        self.groups = set(groups)

    @property
    def key(self):
        return self.size

    @key.setter
    def key(self, value):
        self.size = tuple(value)

    @property
    def geom(self):
        return self.size

class SubFrameT(object):
    """SubFrameT represent a static translation"""

    def __init__(self, tx=0.0, ty=0.0, tz=0.0):
        self.m = np.matrix(np.mat(matrices.hTransX(tx).m*matrices.hTransY(ty).m*matrices.hTransZ(tz).m), dtype=np.float)
        self.subframes = []

    def attach(self, frame):
        self.subframes.append(frame)

    def update(self, angles, T):
        self.T = T*self.m
        for frame in self.subframes:
            frame.update(angles, self.T)

    def bodies(self):
        _bodies = []
        for subframe in self.subframes:
            _bodies += subframe.bodies()
        return _bodies


class BodyTree(object):

    def __init__(self, smodel):
        self.smodel = smodel
        self.frames = [[] for _ in smodel.hms]
        self.hms_f = [sympy.lambdify(smodel.params, hm) for hm in self.smodel.hms]

    def bodies(self):
        _bodies = []
        for frame in self.frames:
            for subframe in frame:
                _bodies += subframe.bodies()
        return _bodies

    def attach(self, frame, joint):
        """
            :param joint:  the index of the joint (int)
        """
        self.frames[joint].append(frame)

    def update(self, angles):
        assert type(angles) != dict
        d_angles = {s: a for s, a in zip(self.smodel.params, angles)}
        for frame_group, hm_f in zip(self.frames, self.hms_f):
            hm = hm_f(*angles)
            for f in frame_group:
                f.update(d_angles, hm)
