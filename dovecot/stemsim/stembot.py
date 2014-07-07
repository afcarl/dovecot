from __future__ import division, print_function, absolute_import
import time

from toolbox import gfx
import powerswitch as ps
import pydyn

from . import stemcfg
from . import stemcom


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

        # clean state for motors
        self._onoff(**kwargs)
        self.stemcom = stemcom.StemCom(cfg, **kwargs)

    def _onoff(self, **kwargs):
        if self.cfg.execute.hard.powerswitch:
            self.stemcom = stemcom.StemCom(self.cfg, **kwargs)
            self.stemcom.rest()
            self.powerswitch.set_off(self.powerswitch_port)
            time.sleep(1)
            self.powerswitch.set_on(self.powerswitch_port)
            time.sleep(1)
            self.stemcom.close()


    def _execute(self, motor_command):

        motor_trajs, _ = motor_command

        try:
            self.stemcom.setup(self.cfg.mprim.init_states, blocking=True)
            time.sleep(0.1)

            assert all(not c for c in self.stemcom.ms.compliant)
            self.stemcom.ms.torque_limit = TORQUE_LIMIT

            max_t = max(tj.max_t for tj in motor_trajs)
            start_time = time.time()
            while time.time()-start_time < max_t:
                self.stemcom.step(motor_trajs, time.time()-start_time)
            end_time = time.time()

            self.stemcom.setup(self.cfg.mprim.init_states, blocking=False)

            return start_time, end_time

        except pydyn.MotorError as exc:
            print('{}{}{}'.format(gfx.red, exc, gfx.end))
            if self.cfg.execute.hard.powerswitch:
                self.powerswitch.set_off(self.powerswitch_port)
            import traceback
            traceback.print_exc()
            raise exc


    def close(self, rest=True):
        if rest:
            self.stemcom.rest()
        self.stemcom.close()
