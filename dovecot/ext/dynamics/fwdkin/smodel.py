"""Symbolic Model module"""
import cPickle

import sympy
from . import matrices as mt

class SymbolicRevoluteJoint(object):

    def __init__(self, d, theta, r, alpha, params=None, constants=None):
        self.params = params or []
        self.constants = constants or []
        self.m   = mt.hTransZ(d).m*mt.hRotZ(theta).m*mt.hTransX(r).m*mt.hRotX(alpha).m
        self.inv = mt.hRotX(alpha).inv*mt.hTransX(r).inv*mt.hRotZ(theta).inv*mt.hTransZ(d).inv


class SymbolicModel(object):

    def __init__(self, simplify=True):
        self.simplify   = simplify
        self.constants  = []
        self.params     = []
        self.joints_sym = [SymbolicRevoluteJoint(0, 0, 0, 0)]
        self.joints     = [SymbolicRevoluteJoint(0, 0, 0, 0)]
        self.hms_sym    = [sympy.eye(4)]
        self.hms        = [sympy.eye(4)]
        self.functional = False

    def __len__(self):
        return len(self.joints)

    def add_joint(self, joint):
        self.joints.append(joint)
        self.joints_sym.append(joint)
        self.constants += joint.constants
        self.params    += joint.params
        self.hms.append(self.hms[-1]*joint.m)
        if self.simplify:
            self.hms[-1] = sympy.trigsimp(self.hms[-1])
        self.hms_sym.append(self.hms[-1])
        self.functional = False

    @property
    def m(self):
        return self.hms[-1]

    def f(self, *args):
        if not self.functional:
            self.functionnalize()
        return self.hms_f[-1](*args)

    def subs_constants(self, d):
        for i, hm_sym in enumerate(self.hms_sym):
            self.hms[i] = hm_sym.subs(d)
        for i, joint_sym in enumerate(self.joints_sym):
            self.joints[i].m = joint_sym.m.subs(d)

    def save(self, filename):
        with open(filename, 'wb') as f:
            cPickle.dump(self, f)

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'rb') as f:
            return cPickle.load(f)

    def functionnalize(self):
        self.hms_f = [sympy.lambdify(self.params, hms) for hms in self.hms]
        self.functional = True
