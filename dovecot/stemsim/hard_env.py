from __future__ import print_function, division, absolute_import
import time
import sys
import atexit

from toolbox import gfx
import natnet
import environments
from environments import tools

from ..vrepsim import sim_env
from . import triopost
from . import stembot
from . import stemcfg

# trio framebuffer buffer duration in seconds.
FB_DURATION = 40.0


class HardwareEnvironment(sim_env.SimulationEnvironment):

    def __init__(self, cfg, verbose=True, optitrack=True):
        super(HardwareEnvironment, self).__init__(cfg)

        self.verbose = verbose
        self.optitrack = optitrack

        self.stem = stemcfg.stems[self.cfg.execute.hard.uid]
        self.M_trans = triopost.load_triomatrix(self.stem)

        atexit.register(self.close)

        if self.verbose:
            print("{}launching serial... {}".format(gfx.purple, gfx.end))
        self.sb = stembot.StemBot(cfg)
        if self.verbose:
            print("{}launching optitrack capture on {}... {}".format(gfx.purple, self.stem.optitrack_addr, gfx.end))
        self.fb = natnet.FrameBuffer(FB_DURATION, addr=self.stem.optitrack_addr)
        if self.verbose:
            print("{}launching vrep... {}".format(gfx.cyan, gfx.end))

        cfg.execute.simu.load = False # FIXME probably not the most elegant


    def _execute_raw(self, motor_command, meta=None):

        meta = {} if meta is None else meta
        tries = meta.get('tries', 3)
        t     = meta.get('t', None)

        try:

            log =  {}
            meta['log'] = log
            log['motor_command'] = motor_command
            #log['scene'] = 'ar_{}'.format(self.cfg.sprims.scene)

            if self.verbose:
                print("{}executing movement on stem...{}".format(gfx.purple, gfx.end), end='\r')
            sys.stdout.flush()

            start_stem = time.time()

            # execute movement on stem
            self.fb.track(self.stem.optitrack_side)
            start, end = self.sb._execute(motor_command)
            self.fb.stop_tracking()
            log['order_time'] = end - start

            if self.verbose:
                print('')
            time.sleep(0.01)
            stem_time = time.time() - start_stem
            print('time slice: {:.1f}'.format(end-start))

            start_vrep = time.time()

            # get optitrack trajectory
            opti_traj = self.fb.tracking_slice(start, end)

            log['opti_traj'] = opti_traj

            # fill gaps
            try:
                opti_traj = triopost.fill_gaps(opti_traj)
            except AssertionError:
                raise natnet.MarkerError

            vrep_traj = triopost.opti2vrep(opti_traj, self.M_trans)

            if self.verbose:
                print("{}executing movement in vrep...{}".format(gfx.cyan, gfx.end))

            # execute in vrep
            """#TODO max_steps set to None ??"""
            raw_sensors = self.vrepcom.run_simulation(vrep_traj, None)

            log['raw_sensors'] = raw_sensors
            log['vrep_traj'] = vrep_traj

            # produce sensory feedback
            raw_sensors = self._process_sensors(raw_sensors)
            vrep_time = time.time() - start_vrep

            log['vrep_time'] = vrep_time

            return raw_sensors

        except stembot.CollisionError:
            if tries > 0:
                self.fb.stop_tracking()
                meta['tries'] -= 1
                return self._execute(motor_command, meta=meta)
            else:
                self.fb.stop_tracking()
                raise self.OrderNotExecutableError

        except natnet.MarkerError as e:
            if tries > 0:
                print('{}caught marker error...                   {}'.format(gfx.red, gfx.end))
                print('{}{}{}'.format(gfx.red, e, gfx.end))
                time.sleep(0.1)
                self.fb = natnet.FrameBuffer(FB_DURATION, addr=self.stem.optitrack_addr)
                meta['tries'] -= 1
                return self._execute(motor_command, meta=meta)
            else:
                raise self.OrderNotExecutableError('{}'.format(e))

    def close(self):
        try:
            self.sb.close()
        except Exception:
            pass
        try:
            self.fb.stop()
            self.fb.join()
        except Exception:
            pass
        try:
            self.vrepcom.close(kill=True)
        except Exception:
            pass
