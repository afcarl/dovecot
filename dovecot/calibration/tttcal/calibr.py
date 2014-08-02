from __future__ import print_function, division, absolute_import
import os

import forest
from toolbox import gfx

from ...vrepsim import vrepcom
from ... import ttts
from ...cfgdesc import desc

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

        cfg.sprims.scene = name
        com = vrepcom.VRepCom(cfg, calcheck=not calibrate, setup=False)
        if calibrate:
            com.caldata = calibrate_scene(com)
        com.close(kill=True)
        return com.caldata

def compare_calib_data(ar_calib, v_calib, vizu_calib):
    assert round(ar_calib.mass, 4) == round(v_calib.mass, 4) == round(vizu_calib.mass, 4), "Toy mass error..."
    assert [round(e, 4) for e in ar_calib.dimensions] == [round(e, 4) for e in v_calib.dimensions] == [round(e, 4) for e in vizu_calib.dimensions], "Toy dimensions error..."
    assert [round(e, 4) for e in ar_calib.position] == [round(e, 4) for e in v_calib.position] == [round(e, 4) for e in vizu_calib.position], "Toy position error..."
    if len(ar_calib.dimensions_m) == len(v_calib.dimensions_m):
        assert ar_calib.dimensions_m   == v_calib.dimensions_m   , "Marker dimensions error..."
    #assert ar_calib.position_world == v_calib.position_world , "Toy position error..."

def object_properties(vrep, handle):
    min_x = vrep.simGetObjectFloatParameter(handle,   21)[0] * 100
    max_x = vrep.simGetObjectFloatParameter(handle,   24)[0] * 100
    min_y = vrep.simGetObjectFloatParameter(handle,   22)[0] * 100
    max_y = vrep.simGetObjectFloatParameter(handle,   25)[0] * 100
    min_z = vrep.simGetObjectFloatParameter(handle,   23)[0] * 100
    max_z = vrep.simGetObjectFloatParameter(handle,   26)[0] * 100
    mass  = vrep.simGetObjectFloatParameter(handle, 3005)[0] * 100

    dims = [max_x - min_x, max_y - min_y, max_z - min_z]

    return dims, mass


def calibrate_scene(com):
    toy_h        = com.vrep.simGetObjectHandle("toy")
    base_h       = com.vrep.simGetObjectHandle("base")
    marker_h     = com.vrep.simGetObjectHandle("marker")
    solomarker_h = com.vrep.simGetObjectHandle("solomarker")

    toy_pos        = com.vrep.simGetObjectPosition(toy_h, base_h)
    toy_pos_world  = com.vrep.simGetObjectPosition(toy_h, -1)

    toy_dims, toy_mass = object_properties(com.vrep, toy_h)

    assert marker_h != -1
    mark_dims, mark_mass = object_properties(com.vrep, marker_h)

    if solomarker_h != -1:
        solo_dims, solo_mass = object_properties(com.vrep, solomarker_h)
        assert solo_dims == mark_dims
        assert solo_mass == mark_mass

    position       = [100 * e for e in toy_pos]
    position_world = [100 * e for e in toy_pos_world]

    scene_filepath = ttts.TTTFile(com.scene_name).filepath
    if not os.path.isfile(scene_filepath):
        print('{}cal: {}error{}: scene file {} not found'.format(gfx.grey, gfx.red, gfx.end, scene_filepath))
        return None
    else:
        caldata = ttts.TTTCalibrationData(com.scene_name, com.cfg.execute.simu.calibrdir)
        caldata.populate(toy_mass, position, toy_dims, toy_pos_world, mark_dims)
        print(caldata.md5)
        caldata.save()
        return caldata


def calibr(names):
    for name in names:
        calib = process_scene(name, calibrate=True)

def test(names):
    for name in names:
        calib = process_scene(name, calibrate=False)
