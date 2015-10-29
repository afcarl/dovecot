from __future__ import print_function, division, absolute_import
import os

import forest
from toolbox import gfx

from ...vrepsim import vrepcom
from ... import ttts
from ...cfgdesc import desc, objdesc

from ...vizu import vrepvizu


cfg = desc._copy(deep=True)
cfg.execute.is_simulation    = True
cfg.execute.simu.ppf         = 10
cfg.execute.simu.headless    = True
cfg.execute.simu.vglrun      = False
cfg.execute.simu.calibrdir   = '~/.dovecot/tttcal/'
cfg.execute.simu.mac_folder  = '/Applications/VRep/vrep.app/Contents/MacOS/'

#cfg.execute.simu.mac_folder  ='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'
cfg.execute.simu.load        = True
cfg.execute.prefilter = False

# cfg.execute.scene.objects.'ball25'
# cfg.execute.scene.object.mass = None
# cfg.execute.scene.object.pos  = (None, None, None)


OBJ_NAMES = ['ball25', 'ball45', 'ball45_2', 'ball', 'blueball', 'ball45_light',
             'cube25', 'cube45',
             'tube40_80']
             #'ball15', 'ball25', 'ball45', 'ball45_2', 'ball45_3', 'ball45_light', 'ball60', 'ball90',
             #'cube25', 'cube45', 'cube90', 'cube140',
             #'tube40_80', 'x_objwall', 'y_objwall', 'y_armwall150']


def process_scene(name, calibrate=True):
    """Calibrate or check scene"""
    # check if caldata is uptodate:
    try:
        caldata = ttts.TTTCalibrationData(name, cfg.execute.simu.calibrdir)
        caldata.load()
        print('{}cal: {}already uptodate{}'.format(gfx.grey, gfx.green, gfx.end))
        return caldata
    except (IOError, AssertionError) as e:
        if isinstance(e, IOError):
            print('{}cal: {}{} could not be read{}'.format(gfx.grey, gfx.yellow, caldata.cal_filepath, gfx.end))
        if isinstance(e, AssertionError):
            print('{}cal: {}mismatching md5 signature{}'.format(gfx.grey, gfx.yellow, gfx.end))

        cfg.execute.scene.name = name
        com = vrepcom.VRepCom(cfg, calcheck=not calibrate, setup=False)
        if calibrate:
            com.caldata = calibrate_scene(com)
        com.close(kill=True)
        return com.caldata



def calibrate_scene(com):
    base_h       = com.vrep.simGetObjectHandle("base")
    marker_h     = com.vrep.simGetObjectHandle("marker")
    solomarker_h = com.vrep.simGetObjectHandle("solomarker")

    marker_pos_w     = tuple(100*p for p in com.vrep.simGetObjectPosition(marker_h, -1))
    solomarker_pos_w = tuple(100*p for p in com.vrep.simGetObjectPosition(solomarker_h, -1))
    robot_pos_w      = tuple(100*p for p in com.vrep.simGetObjectPosition(base_h, -1))
    assert sum(abs(p_r - p_sr)**2 for p_r, p_sr in zip(marker_pos_w, solomarker_pos_w)) < 0.01

    assert marker_h != -1
    mark_dims, mark_mass = ttts.VRepObject.object_properties(com.vrep, marker_h)

    if solomarker_h != -1:
        solo_dims, solo_mass = ttts.VRepObject.object_properties(com.vrep, solomarker_h)
        assert solo_dims == mark_dims
        #assert solo_mass == mark_mass

    objects = {}
    for name in OBJ_NAMES:
        print(name)
        obj = ttts.VRepObject(name)
        obj.load(com, base_h)
        objects[name] = obj

    scene_filepath = ttts.TTTFile(com.scene_name).filepath
    if not os.path.isfile(scene_filepath):
        print('{}cal: {}error{}: scene file {} not found'.format(gfx.grey, gfx.red, gfx.end, scene_filepath))
        return None
    else:
        caldata = ttts.TTTCalibrationData(com.scene_name, com.cfg.execute.simu.calibrdir)
        caldata.populate(objects, robot_pos_w, mark_dims)
        print(caldata.md5)
        caldata.save()
        return caldata


def calibr(names):
    for name in names:
        calib = process_scene(name, calibrate=True)

def test(names):
    for name in names:
        calib = process_scene(name, calibrate=False)
