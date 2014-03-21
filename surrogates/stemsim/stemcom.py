from __future__ import print_function, division

import os
import time
import numpy as np

import forest
from pydyn.msets import MotorSet

import stemcfg

defcfg = forest.Tree()
defcfg['stem.motor_range'] = (0, 253)
defcfg['stem.verbose_dyn'] = True

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
        pose_range = tuple(max(zp-a_min, min(zp+a_max, p)) for p, zp, (a_min, a_max)
                           in zip(values, self.zero_pose, self.angle_ranges))
        # we apply zero_pose
        unzeroed = tuple(v+zp for v, zp in zip(pose_range, self.zero_pose))
        # we enforce angle_limits
        pose_limits = tuple(max(a_min, min(a_max, p)) for p, (a_min, a_max)
                           in zip(unzeroed, self.angle_limits))
        for m, p in zip(self.motors, pose_limits):
            m.position = p


class StemCom(object):

    def __init__(self, cfg, timeout=10):
        self.cfg = cfg
        self.cfg._update(defcfg, overwrite=False)

        self.stemcfg = stemcfg.stems[cfg.stem.uid]
        if os.uname()[0] == 'Linux':
            self.stemcfg.cycle_usb()

        self.ms = RangedMotorSet(  serial_id=self.stemcfg.serial_id,
                                 motor_range=self.stemcfg.motorid_range,
                                     verbose=self.cfg.stem.verbose_dyn,
                                     timeout=timeout)
        assert len(self.ms.motors) == 6

        self.ms.zero_pose    = self.stemcfg.zero_pose
        self.ms.angle_ranges = self.stemcfg.angle_ranges

    def setup(self, pose, blocking=True):
        """Setup the stem at the correct position"""
        self.ms.compliant    = False
        self.ms.moving_speed = 50
        self.ms.pose         = pose

        if blocking:
            while max(abs(p - tg) for p, tg in zip(self.ms.pose, pose)) > 3:
#                self.ms.moving_speed = (min(50, sp + 5) for sp in self.ms.moving_speed)
                time.sleep(0.02)
#        else:
#            self.ms.moving_speed = 50


    def rest(self):
        self.ms.moving_speed = 50

        rest_pose = np.array([0.0, 96.3, -97.8, 0.0, -46.5, -18.9])

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

    def step(self, trajectory, start_time):
        """Step in a timed trajectory.

            :param trajectory:  a pair of time/pose vectors.
            :param start_time:  when the trajectory started
        """
        now = time.time()
        ts, poses = trajectory

        i = 0
        try:
            while ts[i] < now-start_time:
                i += 1
        except IndexError:
            i = len(ts)-1
        try:
            dp = np.abs(np.array(poses[i]) - np.array(self.ms.pose))
            dt = 1.0/5 # 40 Hz
            speed = dp/dt
            speed = np.clip(speed, 1, 400)
            self.ms.moving_speed = speed
            self.ms.pose = poses[i]
        except ValueError as e:
            print(self.ms.pose)
            print(poses[i])
            import traceback
            traceback.print_exc()
            raise e

    def close(self):
        self.ms.close_all()

    def go_to(self, pose, margin=3.0, timeout=10.0):
        self.ms.pose = pose
        start = time.time()
        while max(abs(p - tg) for p, tg in zip(self.ms.pose, pose)) > margin and time.time()-start<timeout:
            time.sleep(0.05)
        return tuple(p-tg for p, tg in zip(self.ms.pose, pose))
