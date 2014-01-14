import os
import pyvrep
import time

class VrepCom(object):

    def __init__(self, port=1984, load=True, verbose=False, ppf = 10):
        self.connected = False
        self.verbose = verbose
        self.port = port
        self.vrep = pyvrep.PyVrep()
        self.ppf  = ppf
        if load:
            self.load()

    def load(self):
        if not self.connected:
            self.vrep.connect(1984)
            self.connected = True

        scene_file = os.path.expanduser(os.path.join(os.path.dirname(__file__), 'surrogate.ttt'))
        if self.verbose:
            print("Loading v-rep scene {}".format(scene_file))
        self.vrep.simLoadScene(scene_file)
        self.handle_script = self.vrep.simGetScriptHandle("Flower");

    def close(self):
        if self.connected:
            self.vrep.disconnect()

    def run_simulation(self, trajectory, max_steps):
        """
            Trajectory is a list 6 pairs of vectors, each of the same length.
            For each pair:
                1. The first vector is the position of the motor in rad.
                2. The second vector is the max velocity of the motor in rad/s.
        """
        if self.verbose:
            print("Setting parameters...")

        for i, (pos_v, vel_v) in enumerate(trajectory):
            assert len(pos_v) == len(vel_v)
            assert len(vel_v) <= max_steps
            self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Joint_{}_pos".format(i+1), list(pos_v))
            self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Joint_{}_vel".format(i+1), list(vel_v))

        self.vrep.simSetScriptSimulationParameterDouble(self.handle_script, "Max_Sim_Steps", [max_steps])
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
    
        #for i in range(1, 7):
        #    self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Joint_{}_final_pos".format(i))
        #    self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Joint_{}_final_vel".format(i))
            
        quaternions = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Quaternions")
        assert len(quaternions) % 4 == 0
        quaternions = tuple(tuple(quaternions[4*i:4*i+4]) for i in range(int(len(quaternions)/4)))

        positions = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Positions")
        assert len(positions) % 3 == 0
        positions = tuple(tuple(positions[3*i:3*i+3]) for i in range(int(len(positions)/3)))

        velocities = self.vrep.simGetScriptSimulationParameterDouble(self.handle_script, "Object_Positions")
        assert len(velocities) % 3 == 0
        velocities = tuple(tuple(velocities[3*i:3*i+3]) for i in range(int(len(velocities)/3)))

        assert len(positions) == len(quaternions) == len(velocities)
        
        self.vrep.simStopSimulation()

        if self.verbose:
            print("End of simulation.")
