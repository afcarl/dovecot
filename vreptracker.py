import numpy as np

class VRepTracker(object):

    def __init__(self, sim, object_name):
        self.sim = sim
        self.object_name = object_name

        self.sfeats = tuple(range(6))
#        self.Sfeats = tuple(range(7))

    def start(self):
        self._register(self.object_name)

    def _register(self, object_name):
        handle = self.sim.simGetObjectHandle(object_name)
        if handle == -1:
            return False
        else:
            self.handle = handle
            self.sim.simStopSimulation()
            self.sim.registerBackgroundFunction("simGetObjectPosition", [handle])
            self.sim.registerBackgroundFunction("simGetObjectOrientation", [handle])
            #self.sim.registerBackgroundFunction("simGetObjectQuaternion", [handle])
            self.pose # initializing calls
            return True

    def close(self):
        self.sim.unregisterBackgroundFunction("simGetObjectPosition", [handle])
        self.sim.unregisterBackgroundFunction("simGetObjectOrientation", [handle])
        #self.sim.unregisterBackgroundFunction("simGetObjectQuaternion", [handle])

    @property
    def pose(self):
#        return self.sim.simGetObjectPosition(self.handle, -1) + self.sim.simGetObjectQuaternion(self.handle, -1)
        return np.array(self.sim.simGetObjectPosition(self.handle, -1) + self.sim.simGetObjectOrientation(self.handle, -1))
