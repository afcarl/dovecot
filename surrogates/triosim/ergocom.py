import os
import pydyn
import time

class ErgoCom(object):

    def __init__(self, cfg, dt, verbose=False):
        self.cfg = cfg
        self.dt = self.cfg.sim.dt
        self.verbose = self.cfg.sim.verbose_com
        self.dyn  = pydyn.create_controller(verbose = self.cfg.sim.verbose_dyn, motor_range = [0, 6])
        self.motors = self.dyn.motors
        assert len(self.motors) == 6

    def setup_arm(self):
        # setup arm in a consistant way.

    def close(self):
        pass

    def _current_pos(self):
        self._pos = (m.position for m in self.motors)
        return self._pos

    def predict_collisions(self):
        return []

    def run_trial(self, trajectory):
        """
            :param trajectory:  a list of list of target positions, one for each motor.
                                Target positions are expressed with the time interval self.dt
                                between values.


            The episode unfolds in the following way:
                1. Predict collisions. Adjust trajectory accordingly.
                2. Verify the motor temperature. Make compliant and wait if necessary.
                3. Setup and verify start position.
                4. Run the motion while receiving optitrack data (for collisions).
                5. Return joint sensors data.
        """
        # Predict collisions
        # Not supported yet

        # Motor temp
        # Not supported yet

        # Setup position
        target = [t_i[0] for t_i in trajectory]
        for m, tg in zip(self.motors, target):
            m.position = tg

        while max(abs(m.position - tg) for m, tg in zip(self.motors, target)) < 3:
            time.sleep(0.1)
        # FIXME: if too long, make resting and compliant and retry.

        # start trajectory.
        # FIXME: record time or signal optitrack
        start = time.time()
        frame = 0
        total_frame = len(trajectory[0])

        while frame < total_frame:
            now = time.time()
            c_frame = int(math.ceil(now-start/dt))
            for i, m in enumerate(self.motors):
                m.position = trajectory[i][c_frame]
            time.sleep(0.001)

        

        return (joint_sensors)
