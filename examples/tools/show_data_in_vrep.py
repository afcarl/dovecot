"""
    Read a logegr file to print or show value :

    Datas are like this :
        [timestamp, datas[order_time, object_sensors, vrep_time, opti_traj, tip_sensors, joint_sensors, order, effect, vrep_traj]]
"""
from __future__ import print_function, division
import sys

import forest

from dovecot.vrepsim import vrepcom
from dovecot.cfgdesc import desc
from dovecot.logger import logger
from dovecot import ttts
from dovecot.vizu import VizuVrep

cfg = desc._copy(deep=True)
cfg.vrep.ppf         = 200
cfg.vrep.headless    = True
cfg.vrep.vglrun      = False
cfg.vrep.calibrdir   = '~/.dovecot/tttcal/'
cfg.vrep.mac_folder  = '/Applications/V-REP/v_rep/bin'
#cfg.vrep.mac_folder  ='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'
cfg.vrep.load        = True
cfg.sprims.prefilter = False
cfg.logger.folder = '~/.dovecot/logger/'

def load_file(folder, filename):
    l = logger.Logger(folder=folder, filename=filename)
    return l.load()

def not_implemented(datas):
    print("Vrep plots for these data is not implemented yet.")

def start_com(datas):
    com = None
    if len(datas) > 0:
        scene = datas[0]['datas']['scene']
        if scene.startswith('ar_'):
            cfg.sprims.scene = scene[3:]
        elif scene.startswith('vrep_'):
            cfg.sprims.scene = scene[5:]
        else:
            raise NameError(scene)
    com = VizuVrep(cfg, calcheck=False)
    return com

def show_traj_data(datas):
    com = start_com(datas)
    for data in datas:
        coordinates = []
        t_stamp = data['timestamp']
        vrep_traj = data['datas']['vrep_traj']
        col_XYZ = data['datas']['collide_data']
        for traj in vrep_traj:
            coordinates.append(traj[1][0])
            coordinates.append(traj[1][1])
            coordinates.append(traj[1][2])
        if len(col_XYZ) == 3:
            com.add_curve([0, 0, 1, 1], 1, coordinates, 1)
        else:
            com.add_curve([0, 1, 0, 1], 1, coordinates, 10)
    com.draw(ppf=1)

def show_collide_data(datas):
    com = start_com(datas)
    coordinates = []
    trajs = []
    for data in datas:
        col_XYZ = data['datas']['collide_data']
        r_traj = data['datas']['tip_sensors']
        if len(col_XYZ) == 3:
            coordinates.append(col_XYZ[0])
            coordinates.append(col_XYZ[1])
            coordinates.append(col_XYZ[2])
            for coord in r_traj:
                trajs.append(coord)
            com.add_curve([0, 0, 1, 0.5], 2, trajs, 4)
    com.add_spheres_set([0, 1, 0, 1], 0.045, coordinates)
    com.draw(ppf=200)

def list_all_keyword(datas):
    print("All valid keywords :")
    for key in dispatch.keys():
        if dispatch[key] != not_implemented:
            print("  {}".format(key))

dispatch = {
    'order_time': not_implemented,
    'object_sensors': not_implemented,
    'vrep_time': not_implemented,
    'opti_traj': not_implemented,
    'tip_sensors': not_implemented,
    'joint_sensors': not_implemented,
    'order': not_implemented,
    'effect': not_implemented,
    'vrep_traj': show_traj_data,
    'collide_data' : show_collide_data,
    'scene' : not_implemented
}

def main():
    if len(sys.argv) != 3:
        print("usage : python {} <log name> --list".format(sys.argv[0]))
    else:
        folder = cfg.logger.folder
        fname = sys.argv[1]
        option = sys.argv[2]
        datas = load_file(folder, fname)
        if option == "--list":
            list_all_keyword(datas)
        elif option.startswith("--"):
            print("error : {} is not a valid option".format(option))
            print("usage : python {} <log name> --list".format(sys.argv[0]))
        else:
            print("Showing vrep plot for \"{}\"".format(sys.argv[2]))
            try:
                dispatch[option](datas)
            except KeyError:
                print("{} is not a valid keyword.".format(option))

if __name__ == '__main__':
    main()
