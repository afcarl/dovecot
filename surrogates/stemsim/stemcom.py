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

class StemCom(MotorSet):

    def __init__(self, cfg):
        self.cfg = cfg
        self.cfg._update(defcfg, overwrite=False)

        self.stemcfg = stemcfg.stems[cfg.stem.uid]
        if os.uname()[0] == 'Linux':
            self.stemcfg.cycle_usb()

        MotorSet.__init__(self, serial_id=self.stemcfg.serial_id, motor_range=self.stemcfg.motorid_range, verbose=self.cfg.stem.verbose_dyn)
        assert len(self.motors) == 6

        self.zero_pose    = self.stemcfg.zero_pose
        self.angle_ranges = self.stemcfg.angle_ranges
        self.max_torque   = self.stemcfg.max_torque
        self.angle_limits = self.stemcfg.angle_limits

    # def make_non_compliant(self):
    #     for m in self.motors:
    #         m.request_write('torque_enable', True)
    #     time.sleep(0.05)
    #     start = time.time()
    #     while any(self.compliant) and time.time()-start < 1.0:
    #         time.sleep(0.1)
    #     if any(self.compliant):
    #         raise IOError("impossible to set all motor non-compliant ({})".format(self.compliant))


    def setup(self, pose, blocking=True):
        """Setup the stem at the correct position"""
        self.compliant = False

        self.max_speed    = 50
        self.torque_limit = 40
        self.pose         = pose

        if blocking:
            while max(abs(p - tg) for p, tg in zip(self.pose, pose)) > 3:
                time.sleep(0.1)

    def rest(self):
        self.max_speed = 50

        rest_pose = np.array([0.0, 96.3, -97.8, 0.0, -46.5, -18.9])
        #rest_pose = np.array([0.0, -98.0, -54.0, 0.0, 58.0, 0.0])
        old_angle_ranges  = self.angle_ranges
        self.angle_ranges  = [(100, 100) for p in self.pose]


        self.pose = rest_pose
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 20:
            time.sleep(0.05)
        self.max_speed    = 20
        self.torque_limit = 20
        start_time = time.time()
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 2.0 and time.time()-start_time < 1.0:
            time.sleep(0.05)

        self.angle_ranges = old_angle_ranges
        self.compliant = True
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
            self.pose = poses[i]
        except ValueError as e:
            print(self.pose)
            print(poses[i])
            import traceback
            traceback.print_exc()
            raise e
