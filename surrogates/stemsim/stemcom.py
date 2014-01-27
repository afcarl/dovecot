import os
import time
import numpy as np
import treedict

from pydyn.msets import MotorSet


defcfg = treedict.TreeDict()
defcfg.stem.motor_range = (0, 253)
defcfg.stem.verbose_dyn = True

class StemCom(MotorSet):

    def __init__(self, cfg):
        self.cfg = cfg
        self.cfg.update(defcfg, overwrite=False)
        MotorSet.__init__(self, motor_range=self.cfg.stem.motor_range, verbose=self.cfg.stem.verbose_dyn)

        self.zero_pose = np.array((172.7, 150.0, 150.0, 172.7, 150.0, 150.0))
        assert len(self.motors) == 6


    def setup(self, pose):
        """Setup the stem at the correct position"""
        if self.compliant:
            self.compliant = False
        self.range_bounds = [(-100, 100)]*6

        self.max_speed  = 100
        self.max_torque = 100
        self.pose = pose

        while max(abs(p - tg) for p, tg in zip(self.pose, pose)) > 3:
            time.sleep(0.1)
        print("rest pose error: {}".format(max(abs(p - tg) for p, tg in zip(self.pose, pose))))

    def rest(self):
        self.max_speed = 100

        rest_pose = np.array([5.3, 96.3, -97.8, 0.6, -46.5, -18.9])
        #rest_pose = np.array([0.0, -98.0, -54.0, 0.0, 58.0, 0.0])
        self.range_bounds = [(min(p, rp), max(p, rp)) for p, rp in zip(self.pose, rest_pose)]


        self.pose = rest_pose
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 20:
            time.sleep(0.05)
        self.max_speed = 20
        self.max_torque = 5
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
        while ts[i] < now-start_time:
            i += 1
        #print(poses[i])
        self.pose = poses[i]



        # FIXME: if too long, make resting and compliant and retry.


    # def run_trial(self, trajectory):
    #     """
    #         :param trajectory:  a list of list of target positions, one for each motor.
    #                             Target positions are expressed with the time interval self.dt
    #                             between values.


    #         The episode unfolds in the following way:
    #             1. Predict collisions. Adjust trajectory accordingly.
    #             2. Verify the motor temperature. Make compliant and wait if necessary.
    #             3. Setup and verify start position.
    #             4. Run the motion while receiving optitrack data (for collisions).
    #             5. Return joint sensors data.
    #     """
    #     # Predict collisions
    #     # Not supported yet

    #     # Motor temp
    #     # Not supported yet

    #     # Setup position
    #     target = [t_i[0] for t_i in trajectory]
    #     for m, tg in zip(self.motors, target):
    #         m.position = tg

    #     while max(abs(m.position - tg) for m, tg in zip(self.motors, target)) < 3:
    #         time.sleep(0.1)
    #     # FIXME: if too long, make resting and compliant and retry.

    #     # start trajectory.
    #     # FIXME: record time or signal optitrack
    #     start = time.time()
    #     frame = 0
    #     total_frame = len(trajectory[0])

    #     while frame < total_frame:
    #         now = time.time()
    #         c_frame = int(math.ceil(now-start/dt))
    #         for i, m in enumerate(self.motors):
    #             m.position = trajectory[i][c_frame]
    #         time.sleep(0.001)



    #     return (joint_sensors)
