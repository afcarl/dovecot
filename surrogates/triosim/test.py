import natnet
import pyvrep
import time

capture_time = 10 # seconds

nnclient = natnet.NatNetClient()
vrep = pyvrep.PyVrep()
vrep.connect(1984)
handle_script = vrep.simGetScriptHandle("marker")

## Getting frames from OptiTrack Trio
print "Capturing..."
start = time.time()
raw_traj = []
run = True
while run:
    frame = nnclient.receive_frame()
    data = frame.unpack_data()
    print data
    if time.time() - start > 10:
        run = False
## Processing them
exit()
## Running trajectory in Vrep
vrep.simSetScriptSimulationParameterDouble(handle_script, "Trajectory", traj)

vrep.simStartSimulation()
wait = True
while wait:
    time.sleep(0.0001) # probably useless; let's be defensive.
    if vrep.simGetSimulationState() == pyvrep.constants.sim_simulation_paused:
        wait = False
object_sensors = vrep.simGetScriptSimulationParameterDouble(handle_script, "Object_Sensors")
assert len(object_sensors) % (3+3+4) == 0
print object_sensors
vrep.simStopSimulation()

vrep.disconnect()