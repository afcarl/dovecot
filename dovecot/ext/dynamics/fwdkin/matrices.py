import numpy as np

import sympy
from sympy import cos, sin

# def deblock(m):
#     m2 = sympy.Matrix(m.shape[0], m.shape[1], lambda i,j:0)
#     for i in range(m.shape[0]):
#         for j in range(m.shape[1]):
#             m2[i, j] = m[i, j]
#     return m2

# def print_matrix(m):
#     m_print = [["" for _ in range(m.shape[1])] for _ in range(m.shape[0])]
#     for j in range(m.shape[1]):
#         col_width = max(len(m[i,j].__repr__()) for i in range(m.shape[0]))
#         for i in range(m.shape[0]):
#             m_print[i][j] = m[i,j].__repr__().rjust(col_width)

#     for i in range(m.shape[0]):
#         print('{}[{}]{}'.format('[' if i == 0 else ' ',
#                                 ',  '.join(e for e in m_print[i]),
#                                 ']' if i == m.shape[0] - 1 else ',',))


# Rotations
class hRotX(object):
    """Homogeneous, x rotation matrix"""
    def __init__(self, theta, inv=True):
        self.theta  = theta
        self.m = sympy.Matrix([[1,          0,           0, 0],
                               [0, cos(theta), -sin(theta), 0],
                               [0, sin(theta),  cos(theta), 0],
                               [0,          0,           0, 1]])
        if inv:
            self.inv = hRotX(-theta, inv=False).m

class hRotY(object):
    """Homogeneous, y rotation matrix"""
    def __init__(self, theta, inv=True):
        self.theta  = theta
        self.m = sympy.Matrix([[ cos(theta), 0, sin(theta), 0],
                               [          0, 1,          0, 0],
                               [-sin(theta), 0, cos(theta), 0],
                               [          0, 0,          0, 1]])
        if inv:
            self.inv = hRotY(-theta, inv=False).m

class hRotZ(object):
    """Homogeneous, z rotation matrix"""
    def __init__(self, theta,inv=True):
        self.theta  = theta
        self.m = sympy.Matrix([[cos(theta), -sin(theta), 0, 0],
                               [sin(theta),  cos(theta), 0, 0],
                               [         0,           0, 1, 0],
                               [         0,           0, 0, 1]])
        if inv:
            self.inv = hRotZ(-theta, inv=False).m

# Translations
class hTransX(object):
    """Homogeneous, translation matrix"""
    def __init__(self, theta, inv=True):
        self.theta  = theta
        self.m = sympy.Matrix([[1, 0, 0, theta],
                               [0, 1, 0,     0],
                               [0, 0, 1,     0],
                               [0, 0, 0,     1]])
        if inv:
            self.inv = hTransX(-theta, inv=False).m

class hTransY(object):
    """Homogeneous, translation matrix"""
    def __init__(self, theta, inv=True):
        self.theta  = theta
        self.m = sympy.Matrix([[1, 0, 0,     0],
                               [0, 1, 0, theta],
                               [0, 0, 1,     0],
                               [0, 0, 0,     1]])
        if inv:
            self.inv = hTransY(-theta, inv=False).m

class hTransZ(object):
    """Homogeneous, translation matrix"""
    def __init__(self, theta, inv=True):
        self.theta  = theta
        self.m = sympy.Matrix([[1, 0, 0,     0],
                               [0, 1, 0,     0],
                               [0, 0, 1, theta],
                               [0, 0, 0,     1]])
        if inv:
            self.inv = hTransZ(-theta, inv=False).m


_Q = np.matrix([[ 1.0,  1.0,  1.0, 1.0],
               [ 1.0, -1.0, -1.0, 1.0],
               [-1.0,  1.0, -1.0, 1.0],
               [-1.0, -1.0,  1.0, 1.0]])

_Z3 = np.matrix([[0.0, 0.0, 0.0]])
_U = np.matrix([[0.0], [0.0], [0.0], [1.0]])

def sign(a):
    return 1 if a >= 0 else -1

def rot2homogeneous(R):
    return np.vstack([np.hstack([R, _Z3]), _U], dtype=np.float)

def hm2quat(H):
    assert H.shape == (4, 4)
    return rot2quat(H[0:3, 0:3])

def hm2trans(H):
    assert H.shape == (4, 4)
    return np.array(np.mat(H[0:3, 3].T), dtype=np.float)[0]

def hm2rot(H):
    assert H.shape == (4, 4)
    return np.array(np.mat(H[0:3, 0:3].T), dtype=np.float)

def rot2quat(R):
    assert R.shape == (3, 3)
    Q_2 = _Q*np.matrix([R[0,0], R[1,1], R[2,2], 1.0]).T/4
    q0 = np.sqrt(np.float(Q_2[0, 0]))
    q1 = sign(R[2, 1]-R[1, 2])*np.sqrt(np.float(Q_2[1,0]))
    q2 = sign(R[0, 2]-R[2, 0])*np.sqrt(np.float(Q_2[2,0]))
    q3 = sign(R[1, 0]-R[0, 1])*np.sqrt(np.float(Q_2[3,0]))
    return np.array([q0, q1, q2, q3], dtype=np.float)

def quat2rot(q):
    q0, q1, q2, q3 = q[0], q[1], q[2], q[3]
    return np.matrix([[q0*q0 + q1*q1 - q2*q2 - q3*q3,       2*(q1*q2 - q0*q3),       2*(q1*q3 + q0*q2)],
                      [            2*(q1*q2 + q0*q3), q0*q0-q1*q1+q2*q2-q3*q3,       2*(q2*q3 - q0*q1)],
                      [            2*(q1*q3 - q0*q2),       2*(q2*q3 + q0*q1), q0*q0-q1*q1-q2*q2+q3*q3]])


# class HomMatrix(object):
#     """Homogeneous transformation matrix, define the caracteristic of the robot joint."""

#     def __init__(self, alpha, a, d, theta):
#         """
#             :param alpha: (always a constant)
#             :param a:     (always a constant) - also called r.
#             :param d:     (fixed for revolute joints)
#             :param theta: (fixed for prismatic joints)
#             For further details, consult :
#             Section 1.5 "Workspace" of chapter 1 "Kinematics" in Springer Handbook of Robotics, or
#             Virtual Robot Arm Control Model, by D.N.D. Kotteg, Proceedings of the Technical Sessions, 20 (2004) 7-14
#             Video : http://www.youtube.com/watch?v=rA9tm0gTln8
#         """
#         self.t = sympy.Matrix([[a*cos(theta)], [a*sin(theta)], [d]])
#         self.r = RotZ(theta).m*RotX(alpha).m
#         self.m = deblock(sympy.BlockMatrix([[self.r, self.t],
#                                             [sympy.Matrix([[0, 0, 0, 1]]), sympy.Matrix([[1]])]]))
#         self.m_1 = deblock(sympy.BlockMatrix([[self.r.T, -self.r.T*self.t],
#                                             [sympy.Matrix([[0, 0, 0, 1]]), sympy.Matrix([[1]])]]))

