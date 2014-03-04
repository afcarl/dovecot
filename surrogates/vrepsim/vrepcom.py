from __future__ import print_function

import os
import time
import signal
import subprocess
import random
import string
import hashlib
import pyvrep
import pickle

def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hash.update(block)
    return hash.hexdigest()

class SceneToyCalibrationData(object):

    def __init__(self, positions, mass, dimensions, scene):
        self.positions = positions
        self.mass = mass
        self.dimensions = dimensions
        scene_file = os.path.expanduser(os.path.join(os.path.dirname(__file__), 'objscene', scene))
        assert os.path.isfile(scene_file), "scene file {} not found".format(scene_file)
        self.md5 = md5sum(scene_file)
        self.scene = scene

    def check_for_changes(self):
        if md5sum(self.scene) == self.md5:
            return False
        return True

    def save(self):
        with open(self.scene + '.calib', 'wb') as f:
            pickle.dump(self, f)

class VRepCom(object):

    def __init__(self, cfg, port=1984, load=True, verbose=False, vrep_folder=None, ppf=200, calibrate=False):
        self.cfg = cfg
        self.connected = False
        self.verbose = verbose
        self.ppf  = cfg.vrep.ppf
        self.port = port

        self.vrep_proc = None
        self.vrep_folder = vrep_folder
        port = self.launch_sim()

        self.vrep = pyvrep.PyVrep()

        self.scene = None
        self.calib = None

        if load:
            self.load()

        if calibrate:
            self.calibrate_scene()
            self.close()
        self.load_calibration_data()

    def launch_sim(self):
        """Launch a subprocess of V-Rep"""

        # port = random.randint(0, 1000000000)
        # while os.path.exists('/tmp/vrep{}'.format(port)):
        #     port = random.randint(0, 1000000000)
        port = 1984
        lognumber = random.randint(0, 1000000000)
        logname = '/tmp/vreplog{}'.format(lognumber)

        headless_flag = '' # '-h' if self.cfg.vrep.headless else ''
        if os.uname()[0] == "Linux":
            if self.cfg.vrep.headless:
                cmd = "xvfb-run vrep >> {}".format(logname)
            else:
                if self.cfg.vrep.vglrun:
                    cmd = "vglrun vrep >> {}".format(logname)
                else:
                    cmd = "DISPLAY=:0 vrep >> {}".format(logname)
        elif os.uname()[0] == "Darwin":
            cmd = "cd {}; ./vrep >> {}".format(self.vrep_folder, logname)
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

    def load(self, scene=None, script="Flower", augmented_reality=False):
        if not self.connected:
            self.vrep.connect(self.port)
            self.connected = True

        if scene is None:
            if not augmented_reality:
                self.scene='vrep_' + self.cfg.sprims.scene + '.ttt'
            else:
                self.scene='ar_' + self.cfg.sprims.scene + '.ttt'
        else:
            self.scene = scene

        scene_file = os.path.expanduser(os.path.join(os.path.dirname(__file__), 'objscene', self.scene))
        assert os.path.isfile(scene_file), "scene file {} not found".format(scene_file)
        print("loading v-rep scene {}".format(scene_file))
        ret = self.vrep.simLoadScene(os.path.abspath(scene_file)) # os.path.abspath TO BE VERIFIED
        #if ret == -1:
        #    raise IOError
        self.handle_script = self.vrep.simGetScriptHandle(script);

    def close(self, kill=False):
        if self.connected:
            if not kill:
                self.vrep.disconnect()
            else:
                self.vrep.disconnectAndQuit()

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

    def load_calibration_data(self):
        scene_file = os.path.expanduser(os.path.join(os.path.dirname(__file__), 'objscene', self.scene))
        assert os.path.isfile(scene_file), "scene file {} not found".format(scene_file)
        with open(scene_file + '.calib', 'rb') as f:
            self.calib = pickle.load(f)
        assert self.calib.md5 == md5sum(scene_file), "loaded scene calibration ({}) differs from scene ({})".format(scene_file + '.calib',scene_file)


    def calibrate_scene(self):
        toy_h = self.vrep.simGetObjectHandle("toy")
        base_h = self.vrep.simGetObjectHandle("dummy_ref_base")
        min_x = self.vrep.simGetObjectFloatParameter(toy_h, 21)[0] * 100
        max_x = self.vrep.simGetObjectFloatParameter(toy_h, 24)[0] * 100
        min_y = self.vrep.simGetObjectFloatParameter(toy_h, 22)[0] * 100
        max_y = self.vrep.simGetObjectFloatParameter(toy_h, 25)[0] * 100
        min_z = self.vrep.simGetObjectFloatParameter(toy_h, 23)[0] * 100
        max_z = self.vrep.simGetObjectFloatParameter(toy_h, 26)[0] * 100
        dimensions = [max_x - min_x, max_y - min_y, max_z - min_z]
        mass_toy = self.vrep.simGetObjectFloatParameter(toy_h, 3005)[0] * 100
        toy_positions = self.vrep.simGetObjectPosition(toy_h, base_h)
        positions = [100 * e for e in toy_positions]
        self.calib = SceneToyCalibrationData(positions, mass_toy, dimensions, self.scene)
        self.calib.save()


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

        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Trajectory", list(traj_x + traj_y + traj_z))

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

        object_sensors = np.array(self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Sensors"))

        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")

        return (object_sensors, None, None)

