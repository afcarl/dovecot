from __future__ import print_function, division, absolute_import

import time
import math

from ..vrepsim import sim_env
from .. import ttts

from ..vrepsim import vrepcom
from ..collider import collider
from ..collider import stem_bodytree


class KinDisplayCom(vrepcom.VRepCom):

    def __init__(self, cfg, verbose=False, calcheck=True, setup=True):
        self.cfg     = cfg
        self.verbose = verbose
        self.setup   = setup


        self.caldata = ttts.TTTCalibrationData(self.cfg.execute.scene.name, self.cfg.execute.simu.calibrdir)
        self.caldata.load()

        from ..collider import display
        self.display = display.BodyTreeCubes(stem_bodytree.bt)
        self.start_time = None

        self.context = {'x_bounds': ( -300.0,  300.0),
                        'y_bounds': ( -300.0,  300.0),
                        'z_bounds': (    0.0,  400.0)}
        self.tracked_handles = []

    def _update(self):
        assert self.start_time is not None
        tick = int((time.time() - self.start_time)/self.cfg.mprims.dt)
        tick = min(tick, len(self.poses) - 1)
        pose = [math.degrees(p) for p in self.poses[tick]]

        orientation = [  1,  -1,  -1,   1,   1,   1]
        u_angles = [o_i*p_i for p_i, o_i in zip(list(pose), orientation)]
        r_angles = [math.radians(a) for a in u_angles]

        self.display.green()
        contacts = collider.collide(pose)
        for c in contacts:
            self.display.cubes_map[c[1].meta].collides = True
            self.display.cubes_map[c[2].meta].collides = True

    def run_simulation(self, trajectory):
        traj = self._prepare_traj(trajectory)
        traj = traj[traj[0]:]
        assert len(traj) % 6 == 0
        self.poses = [traj[6*i:6*i+6] for i in range(int(len(traj)//6))]

        self.display.add_update_function(self._update)

        self.display.setup()
        self.start_time = time.time()
        self.display.run()

    def close(self, kill=True):
        pass


class KinDisplay(sim_env.SimulationEnvironment):

    com_class = KinDisplayCom

    def _process_sensors(self, raw_sensors):
        return None
