from __future__ import print_function, division
import pickle
import os

from ...ext.toolbox import gfx
from . import opti_calibr

def calibrate(stemcfg, cached_opti=False, cached_vrep=False):
    poses = [(  0.0,   0.0,   0.0,   0.0,   0.0,   0.0),

             # 90
             ( 90.0,   0.0,   0.0,   0.0,   0.0,   0.0),
             ( 90.0,   0.0,   0.0,   0.0,  90.0,   0.0),
             ( 90.0,   0.0,   0.0,   0.0,   0.0,  90.0),
             ( 90.0,   0.0,   0.0,   0.0, -90.0,   0.0),
             ( 90.0,   0.0,   0.0,   0.0,   0.0, -90.0),

             ( 90.0,  90.0, -90.0,   0.0,  90.0,   0.0),
             ( 90.0, -90.0,  90.0,   0.0,  90.0,   0.0),
             ( 90.0,   0.0,   0.0,   0.0,   0.0,   0.0),
             ( 90.0,   0.0,   0.0, -90.0,   0.0,   0.0),

             (  0.0,   0.0,   0.0,   0.0,   0.0,   0.0, False),
             (-90.0,   0.0,   0.0,  90.0,   0.0,   0.0, False),

             # -90
             (-90.0,   0.0,   0.0,   0.0,   0.0,   0.0),

             (-90.0,   0.0,   0.0,   0.0,  90.0,   0.0),
             (-90.0,   0.0,   0.0,   0.0,   0.0,  90.0),
             (-90.0,   0.0,   0.0,   0.0, -90.0,   0.0),
             (-90.0,   0.0,   0.0,   0.0,   0.0, -90.0),

             (-90.0,  90.0, -90.0,   0.0,  90.0,   0.0),
             (-90.0, -90.0,  90.0,   0.0,  90.0,   0.0),
             (-90.0,   0.0,   0.0,   0.0,   0.0,   0.0),
             (-90.0,   0.0,   0.0,  90.0,   0.0,   0.0),


             # 0
             (  0.0,   0.0,   0.0,   0.0,   0.0,   0.0, False),
             (  0.0,  90.0,   0.0,   0.0,   0.0,   0.0),
             (  0.0,   0.0,  90.0,   0.0,   0.0,   0.0),
             (  0.0, -90.0,   0.0,   0.0,   0.0,   0.0),
             (  0.0,   0.0, -90.0,   0.0,   0.0,   0.0),
             (  0.0,   0.0, -90.0,   0.0,  90.0,  90.0),
            ]

    if cached_opti:
        assert False
        with open(os.path.abspath(os.path.join(__file__, '..'))+ '/' + stemcfg.opti_capture_file, 'r') as f:
            reached_poses, opti_res = pickle.load(f)
    else:
        reached_poses, opti_res = opti_calibr.opti_capture(poses, stemcfg)
        with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.opti_capture_file, 'w') as f:
            pickle.dump((reached_poses, opti_res), f)

    for p in reached_poses:
        print(p)

    if cached_vrep:
        assert False
        with open(os.path.abspath(os.path.join(__file__, '..'))+ '/' + stemcfg.vrep_capture_file, 'r') as f:
            vrep_res = pickle.load(f)
    else:
        vrep_res = opti_calibr.vrep_capture(reached_poses)
        vrep_res = [list(v[0]) for v in vrep_res]
        with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.vrep_capture_file, 'w') as f:
            pickle.dump([list(v) for v in vrep_res], f)

    m = opti_calibr.compute_calibration(opti_res, vrep_res)

    with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + stemcfg.calib_file, 'w') as f:
        pickle.dump(m, f)

    return m
