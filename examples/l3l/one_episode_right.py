from __future__ import division, print_function
import time
import random

import treedict

import env
from surrogates.stemsim import stembot
from surrogates.stemsim.calibration import transform
from surrogates.stemsim import optivrepar
from natnet import FrameBuffer

cfg = treedict.TreeDict()

cfg.stem.dt = 0.01
cfg.stem.verbose_com = True
cfg.stem.verbose_dyn = True
cfg.stem.motor_range = [1, 100]

cfg.mprim.name = 'dmpg'
cfg.mprim.motor_steps = 500
cfg.mprim.max_steps   = 500
cfg.mprim.uniformze   = False
cfg.mprim.n_basis     = 2
cfg.mprim.max_speed   = 1.0
cfg.mprim.end_time    = 1.25

cfg.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

sb = stembot.StemBot(cfg)

fb = FrameBuffer(40.0)
print("Launching V-REP (~5s)... ")
ovar = optivrepar.OptiVrepAR()

total = 1
count = 0
start = time.time()

try:
    while count < total:
        try:
            order = tuple(random.uniform(lb, hb) for lb, hb in sb.m_bounds)

            # execute movement on stem
            fb.track_right()
            start, end = sb.execute_order(order)
            fb.stop_tracking()

            # get optitrack trajectory
            trajectory = fb.tracking_slice(start, end)
            count += 1

            # fill gaps
            trajectory = transform.fill_gaps(trajectory)

            # execute in vrep
            object_sensors = ovar.execute(trajectory)

            # produce sensory feedback

        except stembot.CollisionError:
            fb.stop_tracking()

    dur = time.time() - start
finally:
    sb.close()

print("{} movements, {:.1f}s ({:.1f}s per movements)".format(total, dur, dur/total))