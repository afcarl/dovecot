from __future__ import print_function, division
import cPickle
import os

from toolbox import gfx
from . import opti_calibr

def calibrate(stemcfg, cached_opti=False, cached_vrep=False):
    poses = [[  0.0,   0.0,   0.0,   0.0,   0.0,   0.0],
             [ 57.2,  11.6, -10.7,  14.1,   6.0, -17.7],
             [ -4.1,  -9.8,   9.8, -34.9,   5.7, -19.2],
             [ -4.4,  -0.4,   0.0,  -2.6, -69.1, -17.7],
             [ -4.1,   5.1,  -8.9,   2.4,  80.8,  13.6],
             [44.3,  -98.5,  33.6, -15.2,  72.3, -25.1],
             [-3.8,   43.5,  25.7,  -3.8,  72.3, -42.7],
             [-25.8, -98.5,  45.6,  -7.9,  76.7,  -0.1],
             [  0.0, -98.5,  20.1,  -2.0,  64.7, -64.1],
             [ -0.6, -98.5, -54.4,   0.0,  57.9,   0.1],
             [0.0,   -97.5,  43.8,  -1.4,  51.2,   5.1],
            ]

    if cached_opti:
        with open(os.path.abspath(os.path.join(__file__, '..'))+ '/' + stemcfg.opti_capture_file, 'r') as f:
            reached_poses, opti_res = cPickle.load(f)
    else:
        reached_poses, opti_res = opti_calibr.opti_capture(poses, stemcfg)
        with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.opti_capture_file, 'w') as f:
            cPickle.dump((reached_poses, opti_res), f)


    if cached_vrep:
        with open(os.path.abspath(os.path.join(__file__, '..'))+ '/' + stemcfg.vrep_capture_file, 'r') as f:
            vrep_res = cPickle.load(f)
    else:
        vrep_res = opti_calibr.vrep_capture(reached_poses)
        vrep_res = [list(v[0]) for v in vrep_res]
        with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.vrep_capture_file, 'w') as f:
            cPickle.dump([list(v) for v in vrep_res], f)

    m = opti_calibr.compute_calibration(opti_res, vrep_res)

    with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.calib_file, 'w') as f:
        cPickle.dump(m, f)

    return m

def load_calibration(stemcfg):
    with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.calib_file, 'r') as f:
        m = cPickle.load(f)

    return m
