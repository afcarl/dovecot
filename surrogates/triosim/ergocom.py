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
        return [m.position for m in self.motors]

    def predict_collisions

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



        return (joint_sensors)
