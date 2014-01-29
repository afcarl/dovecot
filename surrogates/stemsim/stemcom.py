import os
import time
import numpy as np
import treedict

from pydyn.msets import MotorSet

import stemcfg

defcfg = treedict.TreeDict()
defcfg.stem.motor_range = (0, 253)
defcfg.stem.verbose_dyn = True

class StemCom(MotorSet):

    def __init__(self, cfg):
        self.cfg = cfg
        self.cfg.update(defcfg, overwrite=False)

        self.stemcfg = stemcfg.stems[cfg.stem.uid]
        self.stemcfg.cycle_usb()

        MotorSet.__init__(self, serial_id=self.stemcfg.serial_id, motor_range=self.stemcfg.motorid_range, verbose=self.cfg.stem.verbose_dyn)
        assert len(self.motors) == 6

        self.zero_pose = self.stemcfg.zero_pose
        self.max_torque = self.stemcfg.max_torque
        self.angle_limits = self.stemcfg.angle_limits

    def make_non_compliant(self):
        for m in self.motors:
            m.request_write('torque_enable', True)
        time.sleep(0.05)
        start = time.time()
        while any(self.compliant) and time.time()-start < 1.0:
            time.sleep(0.1)
        if any(self.compliant):
            raise IOError("impossible to set all motor non-compliant ({})".format(self.compliant))

    def setup(self, pose):
        """Setup the stem at the correct position"""
#        if any(self.compliant):
        self.make_non_compliant()

        self.range_bounds = [(-100, 100)]*6

        self.max_speed    = 70
        self.torque_limit = 50
        self.pose = pose

        while max(abs(p - tg) for p, tg in zip(self.pose, pose)) > 3:
            time.sleep(0.1)
        #print("rest pose error: {}".format(max(abs(p - tg) for p, tg in zip(self.pose, pose))))

    def rest(self):
        self.max_speed = 100

        rest_pose = np.array([0.0, 96.3, -97.8, 0.0, -46.5, -18.9])
        #rest_pose = np.array([0.0, -98.0, -54.0, 0.0, 58.0, 0.0])
        self.range_bounds = [(min(p, rp), max(p, rp)) for p, rp in zip(self.pose, rest_pose)]


        self.pose = rest_pose
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 20:
            time.sleep(0.05)
        self.max_speed = 20
        self.torque_limit = 20
        start_time = time.time()
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 2.0 and time.time()-start_time < 1.0:
            time.sleep(0.05)

        self.range_bounds = [(p-5, p+5) for p in self.pose]
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
        #print(poses[i])
        self.pose = poses[i]
