from __future__ import print_function, division, absolute_import
import time
import sys
import atexit

from toolbox import gfx
import natnet
import environments

from ..vrepsim import sim_env
from ..logger import logger
from . import triopost
from . import stembot
from . import stemcfg

# trio framebuffer buffer duration in seconds.
FB_DURATION = 40.0


class HardwareEnvironment(sim_env.SimulationEnvironment):

    def __init__(self, cfg, verbose=True, optitrack=True):
        super(Episode, self).__init__(cfg)

        self.verbose = verbose
        self.optitrack = optitrack

        self.stem = stemcfg.execute.hards[self.cfg.execute.hard.uid]
        self.M_trans = triopost.load_triomatrix(self.stem)
        self.vs = stemsensors.VrepSensors(self.cfg)

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

        self.exhibit_prims()


    def _execute_raw(self, motor_command, meta=None):

        meta = {} if meta is None else meta
        tries = meta.get('tries', 3)
        t     = meta.get('t', None)

        try:

            log =  {}
            log['order'] = order
            #log['scene'] = 'ar_{}'.format(self.cfg.sprims.scene)

            if self.verbose:
                print("{}executing movement on stem...{}".format(gfx.purple, gfx.end), end='\r')
            sys.stdout.flush()

            start_stem = time.time()

            # execute movement on stem
            self.fb.track(self.stem.optitrack_side)
            start, end = self.sb._execute(motor_command)

            self.fb.stop_tracking()

            if (start, end) == (None, None):
                return self.vs.null_feedback
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
            raw_sensors = self.ovar.run_simulation(vrep_traj, None)

            log['raw_sensors'] = raw_sensors
            log['vrep_traj'] = vrep_traj

            # produce sensory feedback
            effect = self.vs.process_sensors(object_sensors, joint_sensors, tip_sensors)
            vrep_time = time.time() - start_vrep

            log['vrep_time'] = vrep_time
            log['effect']    = effect

            #print("{}order:{} {}".format(gfx.purple, gfx.end, gfx.ppv(order)))
            if self.verbose:
                print("{}effect:{} {} (stem: {:.1f}, vrep: {:.1f})".format(gfx.cyan,
                      gfx.end, gfx.ppv(effect, fmt=' .8f'), stem_time, vrep_time))

            if self.use_logger:
                self.logger.log(data_log, step=t)

            return effect

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
            self.ovar.close(kill=True)
        except Exception:
            pass
