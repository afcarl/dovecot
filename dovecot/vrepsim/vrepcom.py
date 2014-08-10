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

        self.connected    = False
        self.scene_loaded = False
        self.ppf          = cfg.execute.simu.ppf

        if not calcheck:
            assert not cfg.execute.prefilter, 'Can\'t skip the calibration check and prefilter collisions. Choose.'

        self.vrep_proc = None
        self.mac_folder = os.path.expanduser(cfg.execute.simu.mac_folder)
        self.port = self.launch_sim()

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

        if os.uname()[0] == "Linux":
            if self.cfg.execute.simu.headless:
                cmd = "xvfb-run -a vrep >> {}".format(logname)
            else:
                if self.cfg.execute.simu.vglrun:
                    cmd = "vglrun vrep >> {}".format(logname)
                else:
                    cmd = "DISPLAY=:0 vrep >> {}".format(logname)
        elif os.uname()[0] == "Darwin":
            flags = ''
            if self.cfg.execute.simu.headless:
                flags = '-h'
            cmd = "cd {}; ./vrep {} >> {}".format(self.mac_folder, flags, logname)
        else:
            raise OSError
        print(cmd)
        self.vrep_proc = subprocess.Popen(cmd, stdout=None, stderr=None,
                                shell=True)
        # self.vrep_proc = subprocess.Popen(cmd, stdout=open(os.devnull, 'wb'), stderr=None,
        #                         shell=True, preexec_fn=os.setsid)
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
        toy_handle = self._vrep_get_handle(self.cfg.execute.scene.object.name)

        if self.cfg.execute.scene.object.mass is not None:
            MASS_PARAM = 3005        # 3005 is mass param
            assert self.vrep.simSetObjectFloatParameter(toy_handle, MASS_PARAM, self.cfg.execute.scene.object.mass) != -1

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

    def _vrep_get_handle(self, name, tries=3, fail=True):
        h, trycount = -1, 0
        while h == -1 and trycount < tries:
            if trycount > 0:
                time.sleep(0.2)
            trycount += 1
            h = self.vrep.simGetObjectHandle(name)
        if fail and h == -1:
            raise IOError("could not get handle for object named '{}'".format(name))
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
                     'vx64_4', 'bbMotorHorn4', 'motor4', 'horn4',
                     'vx64_5', 'bbMotorHorn5', 'motor5', 'horn5',
                     'vx64_6', 'bbMotor6',     'motor6', 'marker_joint', 'marker',
                    ]
        else:
            names = []

        return [self._get_handle(name) for name in names]

    def close(self, kill=False):
        if self.connected:
            if not kill:
                self.vrep.disconnect()
            else:
                self.vrep.disconnectAndQuit()
            self.connected = False


    def _prepare_traj(self, trajectory, max_steps=None):
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
        traj = [float(len(trajectory)), float(self.cfg.mprims.sim_end), np.radians(self.cfg.mprims.max_speed)] # motors_steps, max_steps, max_speed
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
        return list(traj_x + traj_y + traj_z)


    def run_simulation(self, trajectory, max_steps):
        """
            Trajectory is a list 6 pairs of vectors, each of the same length.
            For each pair:
                1. The first vector is the position of the motor in rad.
                2. The second vector is the max velocity of the motor in rad/s.
        """
        #return {}

        if self.verbose:
            print("Setting parameters...")

        traj = self._prepare_traj(trajectory, max_steps)
        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Trajectory", traj)
        self.vrep.simSetSimulationPassesPerRenderingPass(self.ppf)

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

        object_sensors = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Sensors"))
        collide_data   = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Collide_Data"))

        tip_sensors = None
        if self.cfg.sprims.tip:
            if self.cfg.execute.is_simulation:
                tip_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Tip_Sensors")
            else:
                tip_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Marker_Trajectory")

        # assert len(positions) == len(quaternions) == len(velocities)

        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        joint_sensors = None

        return {'object_sensors': object_sensors,
                'joint_sensors': joint_sensors,
                'tip_sensors': tip_sensors,
                'collide_data': collide_data}
