import math
import pyvrep

vrep = pyvrep.PyVrep()
vrep.connect(1984)
vrep.simLoadScene("/Users/pfudal/Stuff/Fabien/surrogates/surrogates/vrepsim/surrogate.ttt")
handleScript = vrep.simGetScriptHandle("Flower");

r = 100
l = [(0.2 * e) * math.pi / 180.0 for e in range(r)]

def toto():

    print "Setting parameters..."
    
    for i in range(1, 7):
        vrep.simSetScriptSimulationParameterDouble(handleScript, "Joint_{}_pos".format(i), l)
        vrep.simSetScriptSimulationParameterDouble(handleScript, "Joint_{}_vel".format(i), l)
        
    max_steps = 200
    vrep.simSetScriptSimulationParameterDouble(handleScript, "Max_Sim_Steps", [max_steps])
    
    print "Simulation started."
    
    vrep.simStartSimulation()
    
    wait = True
    
    while wait:
        if vrep.simGetSimulationState() == pyvrep.constants.sim_simulation_paused:
            wait = False
    
    print "Getting resulting parameters."
    
    #for i in range(1, 7):
    #    vrep.simGetScriptSimulationParameterDouble(handleScript, "Joint_{}_final_pos".format(i))
    #    vrep.simGetScriptSimulationParameterDouble(handleScript, "Joint_{}_final_vel".format(i))
        
    vrep.simGetScriptSimulationParameterDouble(handleScript, "Object_Quaternions")
    vrep.simGetScriptSimulationParameterDouble(handleScript, "Object_Positions")
    vrep.simGetScriptSimulationParameterDouble(handleScript, "Object_Velocities")
    
    vrep.simStopSimulation()

    print "End of simulation."

for i in range (100):
    toto()

vrep.disconnect()