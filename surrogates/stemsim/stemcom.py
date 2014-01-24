import os
import time
import numpy as np

from pydyn.msets import MotorSet

class StemCom(MotorSet):

    def __init__(self, cfg):
        self.cfg = cfg
        MotorSet.__init__(self, motor_range=self.cfg.stem.motor_range, verbose=self.cfg.stem.verbose_dyn)
        assert len(self.motors) == 6


    def setup(self, pose):
        """Setup the stem at the correct position"""
        if self.compliant:
            self.compliant = False

        self.max_speed  = 100
        self.max_torque = 50
        self.pose = pose

        while max(abs(p - tg) for p, tg in zip(self.pose, pose)) > 3:
            time.sleep(0.1)
        print("rest pose error: {}".format(max(abs(p - tg) for p, tg in zip(self.pose, pose))))


    def rest(self):
        self.max_speed = 100
        self.range_bounds = ((50, 240),)*6

        rest_pose = np.array([173.3, 52.0, 98.2, 173.0, 201.8, 149.6])

        speeds = [100, 100, 100, 100, 50, 20]
        poses = [self.pose + float(i)/(len(speeds)-1)*(rest_pose - self.pose) for i, _ in enumerate(speeds)]

        # while max(abs(p - tg) for p, tg in zip(self.pose, pose)) > 10:
        #         time.sleep(0.05)

        self.pose = rest_pose
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 20:
            time.sleep(0.05)
        self.max_speed = 20
        self.max_torque = 5
        while max(abs(p - tg) for p, tg in zip(self.pose, rest_pose)) > 2.0:
            time.sleep(0.05)

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
