from math import cos, sin
import numpy as np


def hom_matrix(d, theta, r, alpha):
    """Homogeneous transformation matrix, define the caracteristic of the robot joint.
        @param d      (fixed for revolute joints)
        @param theta  (fixed for prismatic joints)
        @param r      (constant)
        @param alpha  (constant)
        For further details, consult Section 1.5 of Springer Handbook of Robotics,
        or Virtual Robot Arm Control Model, by D.N.D. Kotteg
    """
    return np.matrix([[ cos(theta),  sin(theta)*cos(alpha),  sin(theta)*sin(alpha),-r*cos(theta)],
                      [-sin(theta),  cos(theta)*cos(alpha),  cos(theta)*sin(alpha), r*sin(theta)],
                      [          0,            -sin(alpha),             cos(alpha),           -d],
                      [          0,                      0,                      0,            1],])

def inverse_hm(d, theta, r, alpha):
    return np.matrix([[           cos(theta),           -sin(theta),           0,             r],
                      [sin(theta)*cos(alpha), cos(alpha)*cos(theta), -sin(alpha), -d*sin(alpha)],
                      [sin(alpha)*sin(theta), sin(alpha)*cos(theta),  cos(alpha),  d*cos(alpha)],
                      [                    0,                     0,           0,             1]])

class RevoluteJoint(object):

    def __init__(self, d, theta, r, alpha, counterclock=False, angular_offset=0.0):
        self.d = d
        self.theta = theta
        self.r = r
        self.alpha = alpha
        self.counterclock = counterclock
        self.offset = angular_offset

    def hm(self, v):
        if self.counterclock:
            v = -v
        return hom_matrix(self.d, self.theta + v + self.offset, self.r, self.alpha)

    def inverse_hm(self, v):
        if self.counterclock:
            v = -v
        return inverse_hm(self.d, self.theta + v + self.offset, self.r, self.alpha)

class Model(object):

    def __init__(self, joints):
        """
            :param joints: we assume joints are ordered in a proximo-distal manner.
        """
        self.joints = joints

    def generate(self, vs):
        raise NotImplementedError
        self.hms_solo = [j.hm(v) for v, j in zip(vs, self.joints)]
        self.hms = [np.matrix(np.identity(4))]
        for hm in self.hms_solo:
            self.hms.append(self.hms[-1]*hm)

    def generate_inverse(self, vs):
        self.ihms_solo = [j.inverse_hm(v) for v, j in zip(vs, self.joints)]
        self.ihms = [np.matrix(np.identity(4))]
        for ihm in self.ihms_solo:
            self.ihms.append(self.ihms[-1]*ihm)

    def mul_v(self, m, v):
        u = np.matrix([list(v)+[1]]).T
        pos = m*u
        return (pos[0,0], pos[1,0], pos[2,0])
