from __future__ import division, print_function
import time
import random
import sys

import forest

from toolbox import gfx
from natnet import FrameBuffer

import env
from surrogates.stemsim import calibration
from surrogates.stemsim import stemsensors
from surrogates.stemsim import stembot
from surrogates.stemsim import optivrepar
from surrogates.stemsim import stemcfg

from cfg import cfg0

cfg0.stem.uid = int(sys.argv[1])
stem = stemcfg.stems[cfg0.stem.uid]
M_trans = calibration.load_calibration(stem)
print("{}launching serial... {}".format(gfx.purple, gfx.end))
sb = stembot.StemBot(cfg0)
vs = stemsensors.VrepSensors(cfg0)

fb = FrameBuffer(40.0, addr=stem.optitrack_addr)
print("{}launching vrep... {}".format(gfx.cyan, gfx.end))
ovar = optivrepar.OptiVrepAR(cfg0,verbose=False)

total = 1 if len(sys.argv) <= 2 else int(sys.argv[2])
count = 0
succes = 0
start_time = time.time()

print('')

try:
    while count < total:
        try:
            order = tuple(random.uniform(lb, hb) for lb, hb in sb.m_bounds)

            print("{}executing movement on stem...{}".format(gfx.purple, gfx.end), end='\r')
            sys.stdout.flush()

            # execute movement on stem
            fb.track(stem.optitrack_side)
            start, end = sb.execute_order(order)
            fb.stop_tracking()
            print('')
            time.sleep(0.01)

            # get optitrack trajectory
            opti_traj = fb.tracking_slice(start, end)
            count += 1

            # fill gaps
            opti_traj = calibration.transform.fill_gaps(opti_traj)
            vrep_traj = calibration.transform.opti2vrep(opti_traj, M_trans)

            print("{}executing movement in vrep...{}".format(gfx.cyan, gfx.end))

            # execute in vrep
            object_sensors, joint_sensors, tip_sensors = ovar.execute(vrep_traj)

            # produce sensory feedback
            effect = vs.process_sensors(object_sensors, joint_sensors, tip_sensors)
            if effect[2] == 1.0:
                succes = succes +1
            #print("{}order:{} {}".format(gfx.purple, gfx.end, gfx.ppv(order)))
            print("{}effect:{} {}".format(gfx.cyan, gfx.end, gfx.ppv(effect)))
            print("{}succes:{} {}".format(gfx.green, gfx.end, succes))

        except stembot.CollisionError:
            fb.stop_tracking()

finally:
    sb.close()

dur = time.time() - start_time

print("{} movements, {:.1f}s ({:.1f}s per movements)".format(total, dur, dur/total))