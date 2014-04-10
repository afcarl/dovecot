from __future__ import print_function, division, absolute_import
import time
import sys
import atexit

from toolbox import gfx
import natnet

from ..vrepsim import vrepcom
from ..logger import logger
from . import triopost
from . import stemsensors
from . import stembot
from . import stemcfg

# trio framebuffer buffer duration in seconds.
FB_DURATION = 40.0

class OrderNotExecutableError(Exception):
    pass

class Episode(object):

    def __init__(self, cfg, verbose=True, optitrack=True):
        self.cfg = cfg
        self.verbose = verbose
        self.optitrack = optitrack

        self.stem = stemcfg.stems[self.cfg.stem.uid]
        self.M_trans = triopost.load_triomatrix(self.stem)
        self.vs = stemsensors.VrepSensors(self.cfg)

        atexit.register(self.close)

        self.use_logger = self.cfg.logger.enabled
        if self.use_logger:
            self.logger = logger.Logger(file_name=self.cfg.logger.file_name, folder=self.cfg.logger.folder, write_delay=self.cfg.logger.write_delay)
            self.logger.start()

        if self.verbose:
            print("{}launching serial... {}".format(gfx.purple, gfx.end))
        self.sb = stembot.StemBot(cfg)
        if self.verbose:
            print("{}launching optitrack capture on {}... {}".format(gfx.purple, self.stem.optitrack_addr, gfx.end))
        self.fb = natnet.FrameBuffer(FB_DURATION, addr=self.stem.optitrack_addr)
        if self.verbose:
            print("{}launching vrep... {}".format(gfx.cyan, gfx.end))

        cfg.vrep.load = False # FIXME probably not the most elegant
        self.ovar = vrepcom.OptiVrepCom(cfg, verbose=verbose)
        self.ovar.load(script="marker", ar=True)

        self.exhibit_prims()

        self.OrderNotExecutableError = OrderNotExecutableError

    def exhibit_prims(self):
        self.s_feats  = self.vs.s_feats
        self.s_bounds = self.vs.s_bounds
        self.s_fixed  = self.vs.s_fixed
        self.s_units  = self.vs.s_units
        self.real_s_bounds = self.vs.real_s_bounds

        self.m_feats = self.sb.m_feats
        self.m_bounds = self.sb.m_bounds

    def execute_order(self, order, tries=0):
        try:

            if self.use_logger:
                data_log = {}
                data_log['order'] = order    

            if self.verbose:
                print("{}executing movement on stem...{}".format(gfx.purple, gfx.end), end='\r')
            sys.stdout.flush()

            start_stem = time.time()
             # execute movement on stem
            self.fb.track(self.stem.optitrack_side)
            start, end = self.sb.execute_order(order)

            self.fb.stop_tracking()

            if (start, end) == (None, None):
                return self.vs.null_feedback

            if self.use_logger:
                order_time = end - start
                data_log['order_time'] = order_time

            if self.verbose:
                print('')
            time.sleep(0.01)
            stem_time = time.time() - start_stem
            print('time slice: {:.1f}'.format(end-start))

            start_vrep = time.time()
            # get optitrack trajectory
            opti_traj = self.fb.tracking_slice(start, end)

            if self.use_logger:
                data_log['opti_traj'] = opti_traj

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
            object_sensors, joint_sensors, tip_sensors, collide_data = self.ovar.run_simulation(vrep_traj, None)

            if self.use_logger:
                data_log['object_sensors'] = object_sensors
                data_log['joint_sensors'] = joint_sensors
                data_log['tip_sensors'] = tip_sensors
                data_log['vrep_traj'] = vrep_traj
                data_log['collide_data'] = collide_data

            # produce sensory feedback
            effect = self.vs.process_sensors(object_sensors, joint_sensors, tip_sensors)
            vrep_time = time.time() - start_vrep

            if self.use_logger:
                data_log['vrep_time'] = vrep_time
                data_log['effect'] = effect

            #print("{}order:{} {}".format(gfx.purple, gfx.end, gfx.ppv(order)))
            if self.verbose:
                print("{}effect:{} {} (stem: {:.1f}, vrep: {:.1f})".format(gfx.cyan, 
                      gfx.end, gfx.ppv(effect, fmt=' .8f'), stem_time, vrep_time))

            if self.use_logger:
                self.logger.log(data_log)

            return effect

        except stembot.CollisionError:
            self.fb.stop_tracking()
            raise OrderNotExecutableError

        except natnet.MarkerError:
            if tries == 0:
                print('{}caught marker error...                   {}'.format(gfx.red, gfx.end))
                time.sleep(0.1)
                self.fb = natnet.FrameBuffer(FB_DURATION, addr=self.stem.optitrack_addr)
                return self.execute_order(order, tries=1)
            else:
                raise OrderNotExecutableError

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