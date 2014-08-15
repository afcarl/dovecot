from __future__ import print_function, division, absolute_import
import os
import time
import subprocess
import random
import string

import numpy as np

import pyvrep

from .. import ttts

CONNECTION_TIMEOUT = 120

class VRepCom(object):
    """
    Communication with a V-REP simulation
    """

    def __init__(self, cfg, verbose=False, calcheck=True, setup=True):
        self.cfg     = cfg
        self.verbose = verbose
        self.setup   = setup

        self.connected       = False
        self.scene_loaded    = False
        self.tracked_objects = []
        self.tracked_handles = []

        if not calcheck:
            assert not cfg.execute.prefilter, 'Can\'t skip the calibration check and prefilter collisions. Choose.'

        self.vrep_proc = None
        self.mac_folder = os.path.expanduser(cfg.execute.simu.mac_folder)
        self.port = self.launch_sim()
        self.objects_pos = {}

        self.vrep = pyvrep.PyVrep()

        self.scene = None

        if cfg.execute.simu.load:
            if self.cfg.execute.is_simulation:
                self.load(script='robot', calcheck=calcheck)
            else:
                self.load(script='solomarker', calcheck=calcheck)


    def __del__(self):
        self.close(kill=True)

    def __exit__(self, etype, evalue, etraceback):
        self.close(kill=True)

    def launch_sim(self):
        """Launch a subprocess of V-Rep"""

        # port = random.randint(0, 1000000000)
        # while os.path.exists('/tmp/vrep{}'.format(port)):
        #     port = random.randint(0, 1000000000)
        rand_log = random.Random()
        rand_log.seed(time.time())
        lognumber = rand_log.randint(0, 1000000000)
        logname = '/tmp/vreplog{}'.format(lognumber)

        flags = ''
        if self.cfg.execute.simu.headless:
            flags = '-h'
        if os.uname()[0] == "Linux":
            if self.cfg.execute.simu.headless:
                cmd = "xvfb-run -a vrep -h >> {} 2>> {}".format(logname, logname+'.err')
            else:
                if self.cfg.execute.simu.vglrun:
                    cmd = "vglrun vrep >> {} 2>> {}".format(logname, logname+'.err')
                else:
                    cmd = "DISPLAY=:0 vrep >> {} 2>> {}".format(logname, logname+'.err')
        elif os.uname()[0] == "Darwin":
            cmd = "cd {}; ./vrep {} >> {} 2>> {}".format(self.mac_folder, flags, logname, logname+'.err')
        else:
            raise OSError
        print(cmd)
        self.vrep_proc = subprocess.Popen(cmd, stdout=None, stderr=None, shell=True)
        time.sleep(1)

        port =  None
        start_time = time.time()

        while port is None:
            if time.time() - start_time > CONNECTION_TIMEOUT:
                raise IOError('Could not read port in vrep logfile {}:\n{}'.format(logname, output))

            print("trying to read {}".format(logname))
            with open(logname, 'r') as f:
                output = f.read()

            prefix = 'INFO : network use endPoint ipc:///tmp/vrep_'
            for line in output.split('\n'):
                if string.find(line, prefix) == 0:
                    port = line[len(prefix):]
                    print("found port {}".format(port))
            time.sleep(2)

        return port

    def flush_proc(self):
        if self.vrep_proc is not None:
            self.vrep_proc.stdout.read()
            self.vrep_proc.stderr.read()

    def load(self, script='robot', calcheck=True):
        """

        :param ar:  if True, load augmented reality scene, else, vrep ones.
        """
        self.scene_name =  self.cfg.execute.scene.name

        # check calibration data
        if calcheck:
            self.caldata = ttts.TTTCalibrationData(self.scene_name, self.cfg.execute.simu.calibrdir)
            self.caldata.load()

        # check vrep connectivity
        if not self.connected:
            if not self.vrep.connect_str(self.port):
                raise IOError("Unable to connect to vrep")
            self.connected = True

        # loading scene
        scene_filepath = ttts.TTTFile(self.scene_name).filepath
        assert os.path.isfile(scene_filepath), "scene file {} not found".format(scene_filepath)

        print("loading v-rep scene {}".format(scene_filepath))
        if self.vrep.simLoadScene(scene_filepath) == -1:
            raise IOError
        self.scene_loaded = True

        if self.setup:
            self.setup_scene(script)

    def setup_scene(self, script):
        assert self.scene_loaded

        self._setup_objects()
        self._setup_robot(script)

    def _setup_objects(self):
        for obj_name, obj_cfg in self.cfg.execute.scene.objects._children_items():
            obj_h   = self._vrep_get_handle(obj_name)
            obj_cal = self.caldata.objects[obj_name]

            if obj_cfg.mass is not None:
                MASS_PARAM = 3005        # 3005 is mass param
                assert self.vrep.simSetObjectFloatParameter(obj_h, MASS_PARAM, obj_cfg.mass) != -1

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

        self.handle_script = self.vrep.simGetScriptHandle(script)


    def _vrep_set_pos(self, handle, handle_rel, pos, tries=10, fail=True):
        r, trycount = -1, 0
        while r == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            r = self.vrep.simSetObjectPosition(handle, handle_rel, [p/100.0 for p in pos])
        if fail and r == -1:
            raise IOError("could not set position for object (handle: '{}')".format(handle))
        return r


    def _vrep_get_handle(self, name, tries=3, fail=True):
        h, trycount = -1, 0
        while h == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            h = self.vrep.simGetObjectHandle(name)
        if fail and h == -1:
            raise IOError("could not get handle for object named '{}'".format(name))
        #print(name, h)
        return h

    def _vrep_del_object(self, handle, tries=3, fail=True):
        r, trycount = -1, 0
        while r == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            r = self.vrep.simRemoveObject(handle)
        if fail and r == -1:
            raise IOError('could not get remove object (handle: {})'.format(handle))
        return r

    def _get_children(self, obj_handle):
        assert self.scene_loaded
        if obj_handle == 'robot':
            names = [          'bbMotor1',     'motor1',
                     'vx64_1', 'bbHorn1',      'horn1',
                     'vx64_2', 'bbMotorHorn2', 'motor2', 'horn2',
                     'vx64_3', 'bbMotorHorn3', 'motor3', 'horn3',
                     'vx28_4', 'bbMotorHorn4', 'motor4', 'horn4',
                     'vx28_5', 'bbMotorHorn5', 'motor5', 'horn5',
                     'vx28_6', 'bbMotor6',     'motor6', 'marker_joint', 'marker',
                    ]
        else:
            names = []

        return [self._vrep_get_handle(name) for name in names]

    def close(self, kill=False):
        if self.connected:
            if not kill:
                self.vrep.disconnect()
            else:
                self.vrep.disconnectAndQuit()
            self.connected = False


    def _prepare_traj(self, trajectory):
        if self.cfg.execute.is_simulation:
            return self._prepare_motor_traj(trajectory)
        else:
            return self._prepare_marker_traj(trajectory)

    def _prepare_motor_traj(self, trajectory):
        """
            In LUA code, a trajectory looks like this :
            # motors_sim_steps = math.floor(Trajectory[1])
            # max_sim_steps    = math.floor(Trajectory[2])
            # max_speed        = Trajectory[3]
            # Trajectory[4] for motor 1, Trajectory[5] for motor 2, etc...
        """
        assert len(trajectory) == self.cfg.mprims.traj_end
        traj = ([float(len(trajectory)), float(self.cfg.mprims.sim_end),
                 np.radians(self.cfg.mprims.max_speed)] +
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
        print(traj_prefix)

        return traj_prefix + traj


    def run_simulation(self, trajectory):
        """
            Trajectory is a list 6 pairs of vectors, each of the same length.
            For each pair:
                1. The first vector is the position of the motor in rad.
                2. The second vector is the max velocity of the motor in rad/s.
        """
        #return {}

        if self.verbose:
            print("Setting parameters...")

        traj = self._prepare_traj(trajectory)
        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "trajectory", traj)
        self.vrep.simSetSimulationPassesPerRenderingPass(self.cfg.execute.simu.ppf)

        self.vrep.simSetFloatingParameter(pyvrep.constants.sim_floatparam_simulation_time_step, self.cfg.mprims.dt)

        self.vrep.simStartSimulation()

        if self.verbose:
            print("Simulation started.")

        wait = True
        while wait:
            time.sleep(0.0001) # probably useless; let's be defensive.
            if self.vrep.simGetSimulationState() == pyvrep.constants.sim_simulation_paused:
                wait = False

        if self.verbose:
            print("Getting resulting parameters.")

        object_sensors = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "object_sensors"))
        collide_data   = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "collide_data"))

        marker_sensors = None
        if self.cfg.sprims.tip:
            marker_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "marker_sensors")

        # assert len(positions) == len(quaternions) == len(velocities)

        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        joint_sensors = None

        return {'object_sensors': object_sensors,
                'joint_sensors' : joint_sensors,
                'marker_sensors'   : marker_sensors,
                'collide_data'  : collide_data}
