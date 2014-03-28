from __future__ import print_function, division, absolute_import
import os

import forest

from ...vrepsim import vrepcom
from ... import ttts
from ...cfgdesc import desc

cfg = desc._copy(deep=True)
cfg.vrep.ppf         = 10
cfg.vrep.headless    = True
cfg.vrep.vglrun      = False
cfg.vrep.calibrdir   = '~/.dovecot/tttcal/'
#cfg.vrep.mac_folder  = '/Applications/V-REP/v_rep/bin'
cfg.vrep.mac_folder  ='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'
cfg.vrep.load        = True
cfg.sprims.prefilter = False

def process_scene(name, ar=True, calibrate=True):
    """Calibrate or check scene"""
    cfg.sprims.scene = name
    if ar:
        com = vrepcom.OptiVrepCom(cfg, calcheck=not calibrate)
    else:
        com = vrepcom.VRepCom(cfg, calcheck=not calibrate)
    if calibrate:
        com.caldata = calibrate_scene(com)
    com.close(kill=True)
    return com.caldata

def compare_calib_data(ar_calib, v_calib):
    assert ar_calib.dimensions == v_calib.dimensions, "Toy dimensions error..."
    assert ar_calib.mass       == v_calib.mass      , "Toy mass error..."
    assert ar_calib.position  == v_calib.position , "Toy position error..."

def calibrate_scene(com):
    toy_h    = com.vrep.simGetObjectHandle("toy")
    base_h   = com.vrep.simGetObjectHandle("dummy_ref_base")
    toy_pos  = com.vrep.simGetObjectPosition(toy_h, base_h)
    min_x    = com.vrep.simGetObjectFloatParameter(toy_h, 21)[0] * 100
    max_x    = com.vrep.simGetObjectFloatParameter(toy_h, 24)[0] * 100
    min_y    = com.vrep.simGetObjectFloatParameter(toy_h, 22)[0] * 100
    max_y    = com.vrep.simGetObjectFloatParameter(toy_h, 25)[0] * 100
    min_z    = com.vrep.simGetObjectFloatParameter(toy_h, 23)[0] * 100
    max_z    = com.vrep.simGetObjectFloatParameter(toy_h, 26)[0] * 100
    toy_mass = com.vrep.simGetObjectFloatParameter(toy_h, 3005)[0] * 100

    dimensions = [max_x - min_x, max_y - min_y, max_z - min_z]
    position  = [100 * e for e in toy_pos]

    scene_filepath = ttts.TTTFile(com.scene_name).filepath
    assert os.path.isfile(scene_filepath), 'error: scene file {} not found'.format(scene_filepath)
    caldata = ttts.TTTCalibrationData(com.scene_name, com.cfg.vrep.calibrdir)
    caldata.populate(toy_mass, dimensions, position)
    caldata.save()

    return caldata


def calibr(names):
    for name in names:
        ar_calib, v_calib = None, None
        try:
            v_calib = process_scene(name, ar=False, calibrate=True)
        except IOError as e:
            print(e)
        try:
            ar_calib = process_scene(name, ar=True, calibrate=True)
        except IOError as e:
            print(e)

        if ar_calib != None and v_calib != None:
            try:
                compare_calib_data(ar_calib, v_calib)
            except AssertionError:
                print(ar_calib)
                print(v_calib)
                print('Calibration datas are not the same for file : vrep_{}.ttt and ar_{}.ttt'.format(name, name))

def test(names):
    for name in names:
        try:
            process_scene(name, ar=False, calibrate=False)
        except Exception as e:
            print(e)
        try:
            process_scene(name, ar=True, calibrate=False)
        except Exception as e:
            print(e)
