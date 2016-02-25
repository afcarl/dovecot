from __future__ import print_function, division, absolute_import

import sympy
from sympy import pi

from ..ext.dynamics.fwdkin import smodel


A, B, C, D, E, F, G = map(sympy.Symbol, ['A', 'B', 'C', 'D', 'E', 'F', 'G'])
phi1, phi2, phi3, phi4, phi5, phi6 = map(sympy.Symbol, ['phi1', 'phi2', 'phi3', 'phi4', 'phi5', 'phi6'])

d_constants = {A: 25.0, B: 56.0, C: 83.0, D: 80.0, E: 68.0, F: 67.0, G: 78.0}

                                  # d,       theta, r, alpha
srj0 = smodel.SymbolicRevoluteJoint(A,           0, 0,     0, constants = [A])
srj1 = smodel.SymbolicRevoluteJoint(B, phi1       , 0, -pi/2, params = [phi1], constants = [B])
srj2 = smodel.SymbolicRevoluteJoint(0, phi2 - pi/2, C,     0, params = [phi2], constants = [C])
srj3 = smodel.SymbolicRevoluteJoint(0, phi3 + pi/2, 0, +pi/2, params = [phi3])
srj4 = smodel.SymbolicRevoluteJoint(D, phi4       , E, +pi/2, params = [phi4], constants = [D,E])
srj5 = smodel.SymbolicRevoluteJoint(0, phi5       , F,     0, params = [phi5], constants = [F])
srj6 = smodel.SymbolicRevoluteJoint(0, phi6       , G,     0, params = [phi6], constants = [G])

sm = smodel.SymbolicModel(simplify=True)
sm.add_joint(srj0)
sm.add_joint(srj1)
sm.add_joint(srj2)
sm.add_joint(srj3)
sm.add_joint(srj4)
sm.add_joint(srj5)
sm.add_joint(srj6)

sm.subs_constants(d_constants)
