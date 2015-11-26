from __future__ import print_function, division, absolute_import
import os
import time
import signal
import subprocess
import random
import string
import ctypes

import numpy as np

import vrep as remote_api

from .. import ttts


CONNECTION_TIMEOUT = 120
ROBOT_ELEMENTS = [          'bbMotor1',     'motor1',
                  'vx64_1', 'bbHorn1',      'horn1',
                  'vx64_2', 'bbMotorHorn2', 'motor2', 'horn2',
                  'vx64_3', 'bbMotorHorn3', 'motor3', 'horn3',
                  'vx28_4', 'bbMotorHorn4', 'motor4', 'horn4',
                  'vx28_5', 'bbMotorHorn5', 'motor5', 'horn5',
                  'vx28_6', 'bbMotor6',     'motor6', 'marker_joint', 'marker',
                 ]

def get_bit(val, idx):
    return (val & (1<<idx)) != 0

class Contact(object):

    def __init__(self, step, contact_names, contact_data):
        self.step       = step
        self.obj_names  = sorted(contact_names)
        self.pos        = contact_data[:3]
        self.force      = contact_data[3:]
        self.force_norm_sq = sum([x*x for x in self.force])

    def __repr__(self):
        return 'Contact({}, {}|{}, {})'.format(self.step, self.obj_names[0], self.obj_names[1], self.force_norm_sq)


class VRepCom(object):
    """
    Communication with a V-REP simulation
    """

    def __init__(self, cfg, verbose=False, calcheck=True, setup=True):
        self.cfg      = cfg
        self.verbose  = verbose
        self.calcheck = calcheck
        self.setup    = setup

        self.connected       = False
        self.scene_loaded    = False
        self.tracked_objects = []
        self.tracked_handles = []
        self.handles         = {}
        self.info = {}

        if not calcheck:
            assert not cfg.execute.prefilter, 'Can\'t skip the calibration check and prefilter collisions. Choose.'

        self.vrep_proc = None
        self.mac_folder = os.path.expanduser(cfg.execute.simu.mac_folder)
        self.launch_sim()
        self.objects_pos = {}

        remote_api.simxFinish(-1)
        self.api_id = remote_api.simxStart('127.0.0.1', self.port, True, False, 5000, 5)

        self.scene = None

        if setup and cfg.execute.simu.load:
            if self.cfg.execute.is_simulation:
                self.setup_scene('robot')
            else:
                self.setup_scene('solomarker')

        # one streaming command so that replies to simxGetInMessageInfo will be up-to-date.
        remote_api.simxGetIntegerParameter(self.api_id,
                                           remote_api.sim_intparam_program_version,
                                           remote_api.simx_opmode_streaming)


    def __del__(self):
        pass
        self.close(kill=True)

    def __exit__(self, etype, evalue, etraceback):
        pass
        self.close(kill=True)

    def launch_sim(self):
        """Launch V-Rep as a subprocess"""

        scene_filepath = self.preload_scenefile()

        self.port = random.randint(2000, 65535) # we avoid the default 19997 port.
        # TODO: figure out if/how port number collision have to be handled

        rand_log = random.Random()
        rand_log.seed(time.time())
        lognumber = rand_log.randint(0, 1000000000)
        logname = '/tmp/vreplog{}'.format(lognumber)
        self.logfile_out = logname + '.out'
        self.logfile_err = logname + '.err'
        log_cmd =  '>> {} 2>> {}'.format(self.logfile_out, self.logfile_err)

        flags = '-gREMOTEAPISERVERSERVICE_{}_FALSE_FALSE'.format(self.port)
        if self.cfg.execute.simu.headless:
            flags += ' -h'

        if os.uname()[0] == "Linux":
            # if self.cfg.execute.simu.headless:
            cmd = "xvfb-run -a vrep {} {} {}".format(flags, scene_filepath, log_cmd)
        elif os.uname()[0] == "Darwin":
            cmd = "cd {}; ./vrep {} {} {}".format(self.mac_folder, flags, scene_filepath, log_cmd)
        else:
            raise OSError

        print(cmd)
        self.vrep_proc = subprocess.Popen(cmd, stdout=None, stderr=None, shell=True, preexec_fn=os.setsid)
        self.scene_loaded = True

    def flush_proc(self):
        if self.vrep_proc is not None:
            self.vrep_proc.stdout.read()
            self.vrep_proc.stderr.read()

    def preload_scenefile(self):
        """Check the scene file calibration file"""
        self.scene_name =  self.cfg.execute.scene.name

        # check calibration data
        if self.calcheck:
            self.caldata = ttts.TTTCalibrationData(self.scene_name, self.cfg.execute.simu.calibrdir, self.cfg.execute.simu.calibr_check)
            self.caldata.load()

        scene_filepath = ttts.TTTFile(self.scene_name).filepath
        assert os.path.isfile(scene_filepath), "scene file {} not found".format(scene_filepath)

        return scene_filepath

    def get_info(self):
        res, v = remote_api.simxGetIntegerParameter(self.api_id,
                                                    remote_api.sim_intparam_program_version,
                                                    remote_api.simx_opmode_oneshot_wait)
        assert res == 0
        self.info['vrep_version'] = v
        res, v = remote_api.simxGetIntegerParameter(self.api_id,
                                                    remote_api.sim_intparam_program_revision,
                                                    remote_api.simx_opmode_oneshot_wait)
        assert res == 0
        self.info['vrep_revision'] = v
        res, v = remote_api.simxGetIntegerParameter(self.api_id,
                                                    remote_api.sim_intparam_platform,
                                                    remote_api.simx_opmode_oneshot_wait)
        assert res == 0
        self.info['vrep_platform'] = ['Windows', 'Darwin', 'Linux'][v]
        res, v = remote_api.simxGetIntegerParameter(self.api_id,
                                                    remote_api.sim_intparam_dynamic_engine,
                                                    remote_api.simx_opmode_oneshot_wait)
        assert res == 0
        self.info['physic_engine'] = ['Bullet', 'ODE', 'Vortex', 'Newton'][v]

        return self.info

    def _setup_simulation(self):
        # assert remote_api.simxSetIntegerParameter(self.api_id,
        #            remote_api.sim_intparam_dynamic_step_divider, self.cfg.execute.simu.ppf,
        #            remote_api.simx_opmode_oneshot_wait) == 0

        assert remote_api.simxSetFloatingParameter(self.api_id,
                   remote_api.sim_floatparam_simulation_time_step, self.cfg.mprims.dt,
                   remote_api.simx_opmode_oneshot_wait) == 0


    def setup_scene(self, script):
        assert self.scene_loaded

        self._setup_simulation()
        self._setup_arena()
        self._setup_objects()
        self._setup_robot(script)

    def _setup_arena(self):
        arena_h   = self._vrep_get_handle(self.cfg.execute.scene.arena.name)
        res, arena_vrep_pos = remote_api.simxGetObjectPosition(self.api_id, arena_h, -1, remote_api.simx_opmode_oneshot_wait)
        assert res == 0
        arena_pos = [a_p if a_p is not None else av_p for a_p, av_p in zip(self.cfg.execute.scene.arena.pos, arena_vrep_pos)]

        x, y, z = arena_pos
        contexts = {'arena6x6x4':    {'x_bounds': ( -300.0 + x,  300.0 + x),
                                      'y_bounds': ( -300.0 + y,  300.0 + y),
                                      'z_bounds': (    0.0 + z,  400.0 + z)},
                    'arena10x10x4':  {'x_bounds': ( -500.0 + x,  500.0 + x),
                                      'y_bounds': ( -500.0 + y,  500.0 + y),
                                      'z_bounds': (    0.0 + z,  400.0 + z)},
                    'arena20x20x10': {'x_bounds': (-1000.0 + x, 1000.0 + x),
                                      'y_bounds': (-1000.0 + y, 1000.0 + y),
                                      'z_bounds': (    0.0 + z, 1000.0 + z)},
                   }

        self.context = contexts[self.cfg.execute.scene.arena.name]

        self._vrep_set_pos(arena_h, -1, arena_pos)
        for floor in ['floor_respondable', 'floor_respondable0', 'floor_respondable1']:
            self._vrep_get_handle(floor)


    def _setup_objects(self):
        for obj_name, obj_cfg in self.cfg.execute.scene.objects._children_items():
            obj_h   = self._vrep_get_handle(obj_name)
            obj_cal = self.caldata.objects[obj_name]

            if obj_cfg.mass >= 0:
                MASS_PARAM = 3005        # 3005 is mass param
                assert remote_api.simxSetObjectFloatParameter(self.api_id, obj_h, MASS_PARAM,
                                                              obj_cfg.mass,
                                                              remote_api.simx_opmode_oneshot_wait) == 0

            obj_cal = self.caldata.objects[obj_name]
            obj_pos = obj_cal.actual_pos(obj_cal.pos_w, obj_cfg.pos)
            self._vrep_set_pos(obj_h, -1, obj_pos)
            self.objects_pos[obj_name] = obj_pos

            if obj_cfg.tracked:
                self.tracked_objects.append(obj_name)
                self.tracked_handles.append(obj_h)

    def _setup_robot(self, script):
        assert script in ('robot', 'solomarker', 'vizu')
        # deleting objects
        for s in ('robot', 'solomarker', 'vizu'):
            if s != script:
                robot_handle = self._vrep_get_handle(s)
                children_handles = self._get_children(s) # should be object_handle
                for h in [robot_handle]+children_handles:
                    self._vrep_del_object(h)

        # self.handle_script = remote_api.simxGetScriptHandle(self.api_id, script,
        #                                                     remote_api.simx_opmode_oneshot_wait)
        for element in ROBOT_ELEMENTS:
            self._vrep_get_handle(element)

    def _vrep_set_pos(self, handle, handle_rel, pos, tries=10, fail=True):
        r, trycount = -1, 0
        while r == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            r = remote_api.simxSetObjectPosition(self.api_id, handle, handle_rel, [p/100.0 for p in pos],
                    remote_api.simx_opmode_oneshot_wait)
        if fail and r == -1:
            raise IOError("could not set position for object (handle: '{}')".format(handle))
        return r


    def _vrep_get_handle(self, name, tries=3, fail=True):
        res, trycount = -1, 0
        while res == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            res, h = remote_api.simxGetObjectHandle(self.api_id, name, remote_api.simx_opmode_oneshot_wait)
        if fail and res == -1:
            raise IOError("could not get handle for object named '{}'".format(name))
        #print(name, h)
        self.handles[h] = name
        return h

    def _vrep_del_object(self, handle, tries=3, fail=True):
        r, trycount = -1, 0
        while r == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            r = remote_api.simxRemoveObject(self.api_id, handle, remote_api.simx_opmode_oneshot_wait)
        if fail and r == -1:
            raise IOError('could not get remove object (handle: {})'.format(handle))
        return r

    def _get_children(self, obj_handle):
        assert self.scene_loaded
        if obj_handle == 'robot':
            names = ROBOT_ELEMENTS
        else:
            names = []

        return [self._vrep_get_handle(name) for name in names]

    def close(self, kill=False):
        if self.connected:
            remote_api.simxStopSimulation(self.api_id, remote_api.simx_opmode_oneshot_wait)
            remote_api.simxFinish(self.api_id)
        self.connected = False
        if kill and self.vrep_proc is not None:
            os.killpg(self.vrep_proc.pid, signal.SIGTERM)


    def _prepare_traj(self, trajectory):
        if self.cfg.execute.is_simulation:
            return self._prepare_motor_traj(trajectory)
        else:
            return self._prepare_marker_traj(trajectory)

    def _prepare_motor_traj(self, trajectory):
        """
            In LUA code, a trajectory looks like this : #NOTTRUEANYMORE #OBSOLETE
            # motors_sim_steps = math.floor(Trajectory[1])
            # max_sim_steps    = math.floor(Trajectory[2])
            # max_speed        = Trajectory[3]
            # Trajectory[4] for motor 1, Trajectory[5] for motor 2, etc...
        """
        assert len(trajectory) <= self.cfg.mprims.traj_end
        traj = ([float(len(trajectory)), float(self.cfg.mprims.sim_end),
                 3*np.radians(self.cfg.mprims.max_speed)] +
                 [float(len(self.tracked_handles))] +
                 [float(obj_h) for obj_h in self.tracked_handles]
               )
        traj = [len(traj)+1] + traj

        for pos_v in trajectory:
            traj.extend(pos_v)
        return traj

    def _prepare_marker_traj(self, trajectory):
        assert len(trajectory) > 0, "Trajectory to prepare is empty."

        ts_ref = trajectory[0][0]
        new_traj = []
        for i in range(len(trajectory)):
            if trajectory[i][0] >= ts_ref:
                new_traj.append(trajectory[i])
                ts_ref = ts_ref + self.cfg.mprims.dt

        ts, pos_raw = zip(*new_traj)
        traj_x, traj_y, traj_z = zip(*pos_raw)
        traj = list(traj_x + traj_y + traj_z)

        traj_prefix = ([float(len(new_traj)), self.cfg.mprims.dt,
                        float(self.cfg.mprims.sim_end)] +
                       [float(len(self.tracked_handles))] +
                       [float(obj_h) for obj_h in self.tracked_handles]
                      )
        traj_prefix = [len(traj_prefix)+1] + traj_prefix

        return traj_prefix + traj

    def simulation_paused(self):
        """Returns True if the simulation is paused but not stopped"""
        res, v = remote_api.simxGetInMessageInfo(self.api_id, remote_api.simx_headeroffset_server_state)
        if res == -1:
            return False
        else:
            return get_bit(v, 0) and get_bit(v, 1)

    def _get_signal(self, name, int_type=False):
        res, s = remote_api.simxGetStringSignal(self.api_id, name,
                                                remote_api.simx_opmode_oneshot_wait)
        assert res == 0, 'getting signal `{}` returned error code {}'.format(name, res)
        if int_type:
            data = remote_api.simxUnpackInts(s)
        else:
            data = remote_api.simxUnpackFloats(s)
        return np.array(data)



    def run_simulation(self, trajectory):
        """
            Trajectory is a list 6 pairs of vectors, each of the same length.
            For each pair:
                1. The first vector is the position of the motor in rad.
                2. The second vector is the max velocity of the motor in rad/s.
        """
        assert remote_api.simxStopSimulation(self.api_id, remote_api.simx_opmode_oneshot_wait) == 0

        if self.verbose:
            print("Setting parameters...")

        traj = self._prepare_traj(trajectory)
        packed_data = remote_api.simxPackFloats(traj)
        raw_bytes = (ctypes.c_ubyte * len(packed_data)).from_buffer_copy(packed_data)
        assert remote_api.simxSetStringSignal(self.api_id, 'trajectory', raw_bytes,
                                              remote_api.simx_opmode_oneshot_wait) == 0

        time.sleep(0.1)
        assert remote_api.simxStartSimulation(self.api_id, remote_api.simx_opmode_oneshot_wait) == 0

        if self.verbose:
            print("Simulation started.")

        time.sleep(0.01)
        while not self.simulation_paused():
            time.sleep(0.005)

        time.sleep(1.0)

        if self.verbose:
            print("Getting resulting parameters.")

        object_sensors = self._get_signal('object_sensors')
        collide_data   = self._get_signal('collide_data')
        contact_data   = self._get_signal('contact_data')
        contact_type   = self._get_signal('contact_type', int_type=True)

        contacts = []
        for i in range(0, len(contact_type), 3):
            step      = contact_type[i]
            obj_names = [self.handles[contact_type[i+1]],self.handles[contact_type[i+2]]]
            data      = contact_data[2*i:2*i+6]
            contacts.append(Contact(step, obj_names, data))

        first_c, last_c = None, None
        max_f, max_c = 0.0, None
        for c in contacts:
            if c.obj_names[0] in self.tracked_objects or c.obj_names[1] in self.tracked_objects:
                if first_c is None:
                    first_c = c
                last_c = c
            if max_f < c.force_norm_sq:
                max_f, max_c = c.force_norm_sq, c
        salient_contacts = {'first': first_c, 'last': last_c, 'max': max_c}

        marker_sensors = None
        if self.cfg.sprims.tip:
            marker_sensors = np.array(remote_api.simxUnpackFloats(
                                          remote_api.simxGetStringSignal(self.api_id, 'marker_sensors',
                                          remote_api.simx_opmode_oneshot_wait)))

        # assert len(positions) == len(quaternions) == len(velocities)

        if self.verbose:
            print("End of simulation.")

        joint_sensors = None

        return {'object_sensors'  : object_sensors,
                'joint_sensors'   : joint_sensors,
                'marker_sensors'  : marker_sensors,
                'collide_data'    : collide_data,
                'contacts'        : contacts,
                'salient_contacts': salient_contacts}
