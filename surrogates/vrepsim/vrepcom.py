from __future__ import print_function

import os
import time
import signal
import subprocess
import random

import pyvrep

class VRepCom(object):

    def __init__(self, port=1984, load=True, verbose=False, headless=False, vrep_folder=None, ppf=200):
        self.connected = False
        self.verbose = verbose
        self.headless = headless
        self.ppf  = ppf
        self.port = port

        self.vrep_proc = None
        if vrep_folder is not None:
            self.vrep_folder = vrep_folder
            port = self.launch_sim()
        
        self.vrep = pyvrep.PyVrep()
        
        if load:
            self.load()

    def launch_sim(self):
        """Launch a subprocess of V-Rep"""

        port = random.randint(0, 1000000000)
        while os.path.exists('/tmp/vrep{}'.format(port)):
            port = random.randint(0, 1000000000)

        headless_flag = '-h' if self.headless else ''
        if os.uname()[0] == "Linux":
            cmd = "cd {}; xvfb-run ./vrep.sh {} -g{}".format(self.vrep_folder, headless_flag, port)
        elif os.uname()[0] == "Darwin":
            cmd = "cd {}; ./vrep {} -g{}".format(self.vrep_folder, headless_flag, port)
        else:
            raise OSError
        self.vrep_proc = subprocess.Popen(cmd, stdout=None, stderr=None,
                                shell=True, preexec_fn=os.setsid)
        # self.vrep_proc = subprocess.Popen(cmd, stdout=open(os.devnull, 'wb'), stderr=None,
        #                         shell=True, preexec_fn=os.setsid)
        time.sleep(10)

        self.port = port
        return port

    def flush_proc(self):
        if self.vrep_proc is not None:
            self.vrep_proc.stdout.read()
            self.vrep_proc.stderr.read()

    def load(self):
        if not self.connected:
            self.vrep.connect(self.port)
            self.connected = True

        scene_file = os.path.expanduser(os.path.join(os.path.dirname(__file__), 'surrogate.ttt'))
        if self.verbose:
            print("Loading v-rep scene {}".format(scene_file))
        self.vrep.simLoadScene(scene_file)
        self.handle_script = self.vrep.simGetScriptHandle("Flower");

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
     
        if self.verbose:
            print("Getting resulting parameters.")

        object_sensors = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Sensors")

        # assert len(positions) == len(quaternions) == len(velocities)
        
        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        joint_sensors = None
        return (object_sensors, joint_sensors)
