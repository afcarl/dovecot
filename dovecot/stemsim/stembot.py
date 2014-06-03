from __future__ import division, print_function, absolute_import
import time

import numpy as np

import powerswitch as ps
import pydyn

from .. import ttts
from .. import prims
from ..collider import maycollide
from ..collider import collider
from . import stemcfg
from . import stemcom

class CollisionError(Exception):
    pass

TORQUE_LIMIT = [50, 50, 50, 70, 50, 50]

class StemBot(object):

    """ This class is responsible of executing the motor primitive only.

        This involves carrying out the movement of the stem, and keeping the motor temp
        low, and solving any hardware problem that may happen.
    """

    def __init__(self, cfg, **kwargs):
        self.cfg = cfg
        # will check if the movement has a possibility of generating a non-null
        # sensory feedback. if not and filter_real_execution is True, it will
        #not be executed.

        if self.cfg.execute.hard.powerswitch:
            stem_cfg = stemcfg.stems[cfg.execute.hard.uid]
            self.powerswitch = ps.Eps4m(mac_address=stem_cfg.powerswitch_mac,
                                        load_config=True)
            self.powerswitch_port = stem_cfg.powerswitch
            if self.powerswitch.is_off(self.powerswitch_port):
                self.powerswitch.set_on(self.powerswitch_port)
                time.sleep(1)
            while self.powerswitch.is_restarting(self.powerswitch_port):
                time.sleep(1)

        self.stemcom = stemcom.StemCom(cfg, **kwargs)


    def _execute(self, motor_command):

        ts, motor_traj = motor_command

        try:
            self.stemcom.setup(self.cfg.mprim.init_states, blocking=True)
            time.sleep(0.1)

            assert all(not c for c in self.stemcom.ms.compliant)
            self.stemcom.ms.torque_limit = TORQUE_LIMIT

            start_time = time.time()
            while time.time()-start_time < ts[-1]:
                self.stemcom.step((ts, motor_traj), start_time)
            end_time = time.time()

            self.stemcom.setup(self.cfg.mprim.init_states, blocking=False)

            return start_time, end_time

        except pydyn.MotorError as e:
            print("MotorError")
            if self.cfg.execute.hard.powerswitch:
                self.powerswitch.set_off(self.powerswitch_port)
            import traceback
            traceback.print_exc()
            raise e


    def close(self, rest=True):
        if rest:
            self.stemcom.rest()
        self.stemcom.close()
