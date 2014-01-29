from __future__ import print_function

import os
import time
import signal
import subprocess
import random
import string

import pyvrep

class VRepCom(object):

    def __init__(self, cfg, port=1984, load=True, verbose=False, headless=False, vrep_folder=None, ppf=200):
        self.cfg = cfg
        self.connected = False
        self.verbose = verbose
        self.headless = headless
        self.ppf  = ppf
        self.port = port

        self.vrep_proc = None
        self.vrep_folder = vrep_folder
        port = self.launch_sim()

        self.vrep = pyvrep.PyVrep()

        if load:
            self.load()

    def launch_sim(self):
        """Launch a subprocess of V-Rep"""

        # port = random.randint(0, 1000000000)
        # while os.path.exists('/tmp/vrep{}'.format(port)):
        #     port = random.randint(0, 1000000000)
        port = 1984
        lognumber = random.randint(0, 1000000000)
        logname = '/tmp/vreplog{}'.format(lognumber)

        headless_flag = '-h' if self.headless else ''
        if os.uname()[0] == "Linux":
            if self.cfg.show_vrep:
                cmd = "DISPLAY=:0 vrep >> {}".format(logname)
            else:
                cmd = "xvfb-run vrep >> {}".format(logname)
        elif os.uname()[0] == "Darwin":
            cmd = "cd {}; ./vrep {} -g{} >> {}".format(self.vrep_folder, headless_flag, port, logname)
        else:
            raise OSError
        print(cmd)
        self.vrep_proc = subprocess.Popen(cmd, stdout=None, stderr=None,
                                shell=True, preexec_fn=os.setsid)
        # self.vrep_proc = subprocess.Popen(cmd, stdout=open(os.devnull, 'wb'), stderr=None,
        #                         shell=True, preexec_fn=os.setsid)
        time.sleep(10)

        with open(logname, 'r') as f:
            output = f.read()

        prefix = 'INFO : network use endPoint ipc:///tmp/vrep'
        for line in output.split('\n'):
            if string.find(line, prefix) == 0:
                port = int(line[len(prefix):])
        print("found port {}".format(port))

        self.port = port
        return port

    def flush_proc(self):
        if self.vrep_proc is not None:
            self.vrep_proc.stdout.read()
            self.vrep_proc.stderr.read()

    def load(self, scene="surrogate.ttt", script="Flower"):
        if not self.connected:
            self.vrep.connect(self.port)
            self.connected = True

        scene_file = os.path.expanduser(os.path.join(os.path.dirname(__file__), scene))
        if self.verbose:
            print("Loading v-rep scene {}".format(scene_file))
        ret = self.vrep.simLoadScene(scene_file)
        #if ret == -1:
        #    raise IOError
        self.handle_script = self.vrep.simGetScriptHandle(script);

    def close(self):
        if self.connected:
            self.vrep.disconnect()
        os.kill(self.vrep_proc.pid, signal.SIGKILL)

    def run_simulation(self, trajectory, max_steps):
        """
            Trajectory is a list 6 pairs of vectors, each of the same length.
            For each pair:
                1. The first vector is the position of the motor in rad.
                2. The second vector is the max velocity of the motor in rad/s.
        """

        if self.verbose:
            print("Setting parameters...")

        traj = [float(len(trajectory[0][0])), float(max_steps), trajectory[0][1]] # motors_steps, max_steps, max_speed
        for i, (pos_v, max_speed) in enumerate(trajectory):
            traj += pos_v

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

        object_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Sensors")


        if self.cfg.sprims.tip:
            tip_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Tip_Sensors")

        # assert len(positions) == len(quaternions) == len(velocities)

        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        joint_sensors = None
        return (object_sensors, joint_sensors, tip_sensors)


class OptiVrepCom(VRepCom):

    def _filter_trajectory(self, trajectory):
        assert len(trajectory) > 0

        ts_ref = trajectory[0][0]
        new_traj = []
        new_traj.append(trajectory[0])
        ts_ref = ts_ref + 0.01 # 10 ms
        for i in range (1, len(trajectory)):
            if(trajectory[i][0] > ts_ref):
                new_traj.append(trajectory[i])
                ts_ref = ts_ref + 0.01
        return new_traj

    def run_trajectory(self, trajectory):
        """

        """
        if self.verbose:
            print("Setting parameters...")

        new_trajectory = self._filter_trajectory(trajectory)

        ts, pos_raw = zip(*new_trajectory)
        traj_x, traj_y, traj_z = zip(*pos_raw)
        timstamps = ts

        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Traj_X", list(traj_x))
        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Traj_Y", list(traj_y))
        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Traj_Z", list(traj_z))

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

        if self.verbose:
            print("Getting resulting parameters.")

        object_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Sensors")

        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        return (object_sensors, None, None)

