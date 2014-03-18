import forest
import traceback

from surrogates.vrepsim import vrepcom

configurations={
    'center_cube',
    'center_cylinder',
    'center_sphere',
    'other_cube',
    'cylinder',
    'calibrate',
}

cfg = forest.Tree()
cfg._branch('vrep')
cfg.vrep.ppf       = 10
cfg.vrep.headless  = False
cfg.vrep.vglrun    = False
cfg.vrep.calibrdir = '~/l2l-files/'
cfg._branch('sprims')

def calibrate_ar_scene(name):
    cfg.sprims.scene = name
    com = vrepcom.OptiVrepCom(cfg, vrep_folder='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS', calibrate = True)
    com.close(kill=True)
    return com.calib

def calibrate_vrep_scene(name):
    cfg.sprims.scene = name
    com = vrepcom.VRepCom(cfg, vrep_folder='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS', calibrate = True)
    com.close(kill=True)
    return com.calib

def test_ar_scene(name):
    cfg.sprims.scene = name
    com = vrepcom.OptiVrepCom(cfg, vrep_folder='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS', calibrate = False)
    com.close(kill=True)
    return com.calib

def test_vrep_scene(name):
    cfg.sprims.scene = name
    com = vrepcom.VRepCom(cfg, vrep_folder='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS', calibrate = False)
    com.close(kill=True)
    return com.calib

def compare_calib_data(ar_calib, v_calib):
    assert ar_calib.dimensions == v_calib.dimensions, "Toy dimensions error..."
    assert ar_calib.mass == v_calib.mass, "Toy mass error..."
    assert ar_calib.positions == v_calib.positions, "Toy position error..."

def calibrate_all():
    for conf in configurations:
        ar_calib, v_calib = None, None
        try:
            v_calib = calibrate_vrep_scene(conf)
        except AssertionError as e:
            traceback.print_exc()
            print "No vrep file for {}".format(conf)
        try:
            ar_calib = calibrate_ar_scene(conf)
        except AssertionError as e:
            traceback.print_exc()
            print "No ar file for {}".format(conf)
        if ar_calib != None and v_calib != None:
            try:
                compare_calib_data(ar_calib, v_calib)
            except:
                ar_calib.print_it()
                v_calib.print_it()
                print "Calibration datas are not the same for file : vrep_{}.ttt and ar_{}.ttt".format(conf, conf)

def test_all():
    for conf in configurations:
        ar_calib, v_calib = None, None
        try:
            v_calib = test_vrep_scene(conf)
        except Exception as e:
            traceback.print_exc()
            print "Calibration error for {}".format(conf)
        try:
            ar_calib = test_ar_scene(conf)
        except Exception as e:
            traceback.print_exc()
            print "Calibration error  for {}".format(conf)

calibrate_all()
#test_all()