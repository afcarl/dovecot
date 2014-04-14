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

    def __init__(self, cfg, verbose=False, calcheck=True):
        self.cfg = cfg
        self.connected = False
        self.verbose = verbose
        self.ppf  = cfg.vrep.ppf
        if not calcheck:
            assert not cfg.sprims.prefilter, 'Can\'t skip the calibration check and prefilter collisions. Choose.'

        self.vrep_proc = None
        self.mac_folder = os.path.expanduser(cfg.vrep.mac_folder)
        self.port = self.launch_sim()

        self.vrep = pyvrep.PyVrep()

        self.scene = None

        if cfg.vrep.load:
            self.load(calcheck=calcheck)


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
            if self.cfg.vrep.headless:
                cmd = "xvfb-run vrep >> {}".format(logname)
            else:
                if self.cfg.vrep.vglrun:
                    cmd = "vglrun vrep >> {}".format(logname)
                else:
                    cmd = "DISPLAY=:0 vrep >> {}".format(logname)
        elif os.uname()[0] == "Darwin":
            cmd = "cd {}; ./vrep >> {}".format(self.mac_folder, logname)
        else:
            raise OSError
        print(cmd)
        self.vrep_proc = subprocess.Popen(cmd, stdout=None, stderr=None,
                                shell=True)
        # self.vrep_proc = subprocess.Popen(cmd, stdout=open(os.devnull, 'wb'), stderr=None,
        #                         shell=True, preexec_fn=os.setsid)
        time.sleep(1)

        port_found = False
        start_time = time.time()
        while(not port_found and time.time() - start_time < CONNECTION_TIMEOUT):
            print("trying to read {}".format(logname))
            with open(logname, 'r') as f:
                output = f.read()

            prefix = 'INFO : network use endPoint ipc:///tmp/vrep_'
            for line in output.split('\n'):
                if string.find(line, prefix) == 0:
                    port = line[len(prefix):]
                    port_found = True
                    print("found port {}".format(port))
            time.sleep(2)
        return port

    def flush_proc(self):
        if self.vrep_proc is not None:
            self.vrep_proc.stdout.read()
            self.vrep_proc.stderr.read()

    def load(self, script="Flower", ar=False, calcheck=True):
        """

        :param ar:  if True, load augmented reality scene, else, vrep ones.
        """
        self.scene_name = '{}_{}'.format({True:'ar', False:'vrep'}[ar], self.cfg.sprims.scene)

        if calcheck:
            self.caldata = ttts.TTTCalibrationData(self.scene_name, self.cfg.vrep.calibrdir)
            self.caldata.load()

        if not self.connected:
            if not self.vrep.connect_str(self.port):
                raise IOError("Unable to connect to vrep")
            self.connected = True

        scene_filepath = ttts.TTTFile(self.scene_name).filepath
        assert os.path.isfile(scene_filepath), "scene file {} not found".format(scene_filepath)

        print("loading v-rep scene {}".format(scene_filepath))
        ret = self.vrep.simLoadScene(scene_filepath)
        #if ret == -1:      #FIXME Why not ?
        #    raise IOError
        self.handle_script = self.vrep.simGetScriptHandle(script)

    def close(self, kill=False):
        if self.connected:
            if not kill:
                self.vrep.disconnect()
            else:
                self.vrep.disconnectAndQuit()
            self.connected = False


    def _prepare_traj(self, trajectory, max_steps):
        traj = [float(len(trajectory[0][0])), float(max_steps), trajectory[0][1]] # motors_steps, max_steps, max_speed
        for i, (pos_v, max_speed) in enumerate(trajectory):
            traj += pos_v
        return traj

    def run_simulation(self, trajectory, max_steps):
        """
            Trajectory is a list 6 pairs of vectors, each of the same length.
            For each pair:
                1. The first vector is the position of the motor in rad.
                2. The second vector is the max velocity of the motor in rad/s.
        """

        if self.verbose:
            print("Setting parameters...")

        traj = self._prepare_traj(trajectory, max_steps)
        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Trajectory", traj)
        self.vrep.simSetSimulationPassesPerRenderingPass(self.ppf)

        self.vrep.simStartSimulation()

        if self.verbose:
            print("Simulation started.")

        wait = True
        while wait:
            time.sleep(0.0001) # probably useless; let's be defensive.
            if self.vrep.simGetSimulationState() == pyvrep.constants.sim_simulation_paused:
                wait = False

        object_sensors = None
        joint_sensors = None
        tip_sensors = None

        if self.verbose:
            print("Getting resulting parameters.")

        object_sensors = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Sensors"))
        collide_data = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Collide_Data"))

        if self.cfg.sprims.tip:
            tip_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Tip_Sensors")

        # assert len(positions) == len(quaternions) == len(velocities)

        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        joint_sensors = None
        return (object_sensors, joint_sensors, tip_sensors, collide_data)


class OptiVrepCom(VRepCom):

    def _prepare_traj(self, trajectory, max_step=None):
        assert len(trajectory) > 0, "Trajectory to prepare is empty."

        ts_ref = trajectory[0][0]
        new_traj = []
        new_traj.append(trajectory[0])
        ts_ref = ts_ref + 0.01 # 10 ms
        for i in range (1, len(trajectory)):
            if trajectory[i][0] > ts_ref:
                new_traj.append(trajectory[i])
                ts_ref = ts_ref + 0.01

        ts, pos_raw = zip(*new_traj)
        traj_x, traj_y, traj_z = zip(*pos_raw)
        return list(traj_x + traj_y + traj_z)

    def load(self, script="marker", ar=True, calcheck=True):
        super(self.__class__, self).load(script, ar, calcheck)

