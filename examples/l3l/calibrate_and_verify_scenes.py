import treedict
import traceback

from surrogates.vrepsim import vrepcom

configurations={
    'center_cube',
    'center_cylinder',
    'center_sphere',
    'other_cube',
    'cylinder'
}

def calibrate_ar_scene(name):
    cfg = treedict.TreeDict()
    cfg.sprims.scene = name
    cfg.vrep.headless = False
    cfg.vrep.vglrun = False
    com = vrepcom.OptiVrepCom(cfg, vrep_folder='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS', calibrate = True)
    return com.calib
    
def calibrate_vrep_scene(name):
    cfg = treedict.TreeDict()
    cfg.sprims.scene = name
    cfg.vrep.headless = False
    cfg.vrep.vglrun = False
    com = vrepcom.VRepCom(cfg, vrep_folder='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS',calibrate = True)
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
        except Exception as e:
            traceback.print_exc()
            print "No vrep file for {}".format(conf)
        try:
            ar_calib = calibrate_ar_scene(conf)
        except Exception as e:
            traceback.print_exc()
            print "No ar file for {}".format(conf)
        if ar_calib != None and v_calib != None:
            try:
                compare_calib_data(ar_calib, v_calib)
            except:
                print "Calibration datas are not the same for file : vrep_{}.ttt and ar_{}.ttt".format(conf)

calibrate_all()