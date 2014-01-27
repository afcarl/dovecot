from __future__ import print_function, division
import cPickle
import os

from toolbox import gfx
from . import opti_calibr

def calibrate(cached=False):
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


    if cached:
        with open(os.path.abspath(os.path.join(__file__, '..'))+'vrep_pos.data', 'r') as f:
            vrep_res = cPickle.read(f)

        # vrep_res =  [[ 0.01100481,  0.6823279 ,  2.45170567],
        #              [ 1.51487219,  2.00143284,  2.44584283],
        #              [-1.10360631,  0.93663345,  2.40484004],
        #              [-0.10239414,  1.52747809,  1.3957642 ],
        #              [-0.01479483,  1.66135542,  3.49237228],
        #              [ 1.79438766,  0.19681993,  0.46468991],
        #              [ 0.03955708,  4.13104251,  3.17516741],
        #              [-1.3426378 , -0.06030752,  1.14177692],
        #              [-0.03712337, -0.01571427, -0.32883829],
        #              [ 0.00571253,  1.94265702, -1.36885245],
        #              [-0.02132425, -0.49028205,  0.64462687]]
    else:
        vrep_res = opti_calibr.vrep_calibration(poses)
        vrep_res = [list(v[0]) for v in vrep_res]
        with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + 'vrep_pos.data', 'w') as f:
            cPickle.dump([list(v) for v in vrep_res], f)
        # print('[{}]'.format(',\n'.join(gfx.ppv(list(v[0]), fmt='+7.4f') for v in vrep_res)))

    m = opti_calibr.opti_calibration(poses, vrep_res)

    with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + 'calib.data', 'w') as f:
        cPickle.dump(m, f)

    return m

def load_calibration():
    with open(os.path.abspath(os.path.join(__file__, '..')) + '/' + 'calib.data', 'r') as f:
        m = cPickle.load(f)

    return m
