import sympy
from sympy import pi

import pyfwdkin

a, b, c, d, e, f, t0, t1, t2, t3, t4, t5 = map(sympy.Symbol, ['a', 'b', 'c', 'd', 'e', 'f', 't0', 't1', 't2', 't3', 't4', 't5'])

# Arm description
# DH parameters         alpha,  r,  d,  theta        (r is also called a)
ergo_desc = ((( -pi/2,  0,  a,  t0       ), t0, (a, 35)),
             ((     0,  b,  0,  t1 - pi/2), t1, (b, 82)),
             ((  pi/2,  0,  0,  t2 + pi/2), t2, (c, 80)),
             (( -pi/2,  d,  c,  t3       ), t3, (d, 65)),
             ((     0,  e,  0,  t4       ), t4, (e, 67)),
             ((     0,  f,  0,  t5       ), t5, (f, 63)))

def create_model(descs):
    dh_params, variables, constants = zip(*descs)
    return pyfwdkin.ForwardModel(dh_params, params=variables, constants=constants)

# stem = create_model(ergo_desc)

# print(stem.hms[1])
# print(stem.hms[1].T)
# print(stem.hms[1]*stem.hms[1].T)
# print(sympy.trigsimp(stem.hms[1]*stem.hms[1].T))
# class ErgoForward(object):
#     """Forward and anticollision system for stems."""
#     pass

from pyfwdkin import matrices


theta = sympy.Symbol('theta')
alpha = sympy.Symbol('alpha')
r = sympy.Symbol('r')
d = sympy.Symbol('d')

hm = matrices.HomMatrix(alpha, r, d, theta)

assert sympy.trigsimp(hm.m*hm.m_1) == sympy.Matrix.eye(4)