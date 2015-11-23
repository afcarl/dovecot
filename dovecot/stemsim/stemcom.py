from __future__ import print_function, division, absolute_import
import os, sys
import time
import threading

import numpy as np

import scicfg
from pydyn.msets import MotorSet

from ..collider import collider
from . import stemcfg

defcfg = scicfg.SciConfig()
defcfg['execute.hard.verbose_dyn'] = True

class ZeroError(Exception):
    """Thrown when a status packet arrived corrupted."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "ZeroError({})".format(self.msg, )




class RangedMotorSet(MotorSet):
    """
    We add an angle range abstraction to MotorSet. It is a way to
    define soft angle_limits, which are enforced when setting MotorSet.pose.
    If angle_limits are more constraining than angle_ranges, those are
    enforced too when calling pose.

    The angle_ranges check can be bypassed by setting the position of each
    motor directly.
    """

    def __init__(self, *args, **kwargs):
        MotorSet.__init__(self, *args, **kwargs)
        angle_ranges = []
        for zp, m in zip(self.zero_pose, self.motors):
            a_min, a_max = m.angle_limits
            angle_ranges.append((zp-a_min, a_max-zp))
        object.__setattr__(self, '_angle_ranges', tuple(angle_ranges))

    @property
    def angle_ranges(self):
        return self._angle_ranges

    @angle_ranges.setter
    def angle_ranges(self, values):
        if not hasattr(values, '__iter__'):
            values = tuple(values for m in self.motors)
        self._angle_ranges = values

    @MotorSet.pose.setter
    def pose(self, values):
        if not hasattr(values, '__iter__'):
            values = tuple(values for m in self.motors)
        # we enforce ranges
        pose_range = tuple(max(zp-a_min, min(zp+a_max, p)) if p is not None else None for p, zp, (a_min, a_max)
                           in zip(values, self.zero_pose, self.angle_ranges))
        # we apply zero_pose
        unzeroed = tuple(v+zp if v is not None else None for v, zp in zip(pose_range, self.zero_pose))
        # we enforce angle_limits
        pose_limits = tuple(max(a_min, min(a_max, p)) if p is not None else None for p, (a_min, a_max)
                           in zip(unzeroed, self.angle_limits))
        for m, p in zip(self.motors, pose_limits):
            if p is not None:
                m.position = p


class StemCom(object):

    def __init__(self, cfg, timeout=10):
        self.cfg = cfg
        self.cfg._update(defcfg, overwrite=False)

        self.stemcfg = stemcfg.stems[cfg.execute.hard.uid]
        if os.uname()[0] == 'Linux':
            self.stemcfg.cycle_usb()

        self.ms = RangedMotorSet(  serial_id=self.stemcfg.serial_id,
                                 motor_range=self.stemcfg.motorid_range,
                                     verbose=self.cfg.execute.hard.verbose_dyn,
                                     timeout=timeout)
        assert len(self.ms.motors) == 6

        self.zero_thread     = None
        self.ms.zero_pose    = self.stemcfg.zero_pose
        self.ms.angle_ranges = self.stemcfg.angle_ranges


    def setup(self, pose, blocking=True):
        """Setup the stem at the correct position"""
        self.ms.moving_speed = 100

        if self.zero_thread is not None:
            self.zero_thread.join()
            self.zero_thread = None

        self.zero_thread = threading.Thread(target=self.careful_zero, args=(pose,))
        self.zero_thread.daemon = True
        self.zero_thread.start()

        if blocking:
            self.zero_thread.join()
            self.zero_thread = None

            if max(abs(p - tg) for p, tg in zip(self.ms.pose, pose[:5])) > 6:
                print("Can't reach zero position")
                raise ZeroError(tuple(abs(p - tg) for p, tg in zip(self.ms.pose, pose)))


    def rest(self):
        assert self.zero_thread is None

        rest_pose = np.array([0.0, 96.3, -97.8, 0.0, -46.5, -10.0])

        self.ms.compliant    = False
        self.ms.moving_speed = 50
        self.ms.pose = rest_pose

        while max(abs(p - tg) for p, tg in zip(self.ms.pose, rest_pose)) > 20:
            time.sleep(0.05)

        self.ms.moving_speed = 20
        self.ms.torque_limit = 20
        start_time = time.time()
        while max(abs(p - tg) for p, tg in zip(self.ms.pose, rest_pose)) > 2.0 and time.time()-start_time < 1.0:
            time.sleep(0.05)

        self.ms.compliant = True
        time.sleep(0.3)

    def step(self, trajectory, t):
        """Step in a timed trajectory.

        :param trajectory: list of Trajectory instances
        :param t         : time since the execution started
        """
        assert self.zero_thread is None

        try:
            pose       = [tj_i.p(t)      for tj_i in trajectory]
            if collider.collide(self.ms.pose):
                return True
            max_speeds = [tj_i.max_speed for tj_i in trajectory]
            dp = np.abs(np.array(pose) - np.array(self.ms.pose))
            dt = 1.0/5 # 40 Hz
            speed = dp/dt
            speed = np.clip(speed, 1, max_speeds)
            self.ms.moving_speed = speed
            self.ms.pose = pose
            return False
        except ValueError as e:
            print(self.ms.pose)
            print(pose)
            import traceback
            traceback.print_exc()
            raise e

    def close(self):
        self.ms.close_all()

    def careful_zero(self, pose, margin=3.0, timeout=10.0, speed=None):
        old_torque = list(self.ms.torque_limit)
        old_speed  = list(self.ms.moving_speed)

        if self.dist([None, 0.0, 0.0, None, None, None]) > 10.0:

            self.ms.compliant    = [True, False, False, True, True, True]
            self.ms.moving_speed = [None,   100,   100, None, None, None]
            self.ms.torque_limit = [None,    50,    50, None, None, None]
            time.sleep(0.2)

            self.go_to([None, 0.0, 0.0, None, None, None])

        self.ms.compliant    = False
        self.ms.torque_limit = 50
        self.ms.speed        = 100
        self.go_to(pose)

        return self.ms.pose

    def dist(self, pose):
        if all(p is None for p in pose):
            return 0.0
        return max(abs(p-tg) for p, tg in zip(self.ms.pose, pose) if tg is not None)

    def go_to(self, pose, margin=3.0, timeout=10.0):
        self.ms.pose = pose
        start = time.time()
        while (time.time() - start < timeout and
               max(abs(p - tg) for p, tg in zip(self.ms.pose, pose) if tg is not None) > margin):
            time.sleep(0.05)
        return tuple(p-tg for p, tg in zip(self.ms.pose, pose) if tg is not None)
