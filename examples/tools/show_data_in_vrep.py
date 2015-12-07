"""
    Read a logegr file to print or show value :

    Datas are like this :
        [timestamp, datas[order_time, object_sensors, vrep_time, opti_traj, tip_sensors, joint_sensors, order, effect, vrep_traj]]
"""
from __future__ import print_function, division
import sys
import os
import random
import time

import scicfg
import dotdot
from dovecot.vrepsim import vrepcom
from dovecot.cfgdesc import desc
from dovecot.logger import logger
from dovecot import ttts
from dovecot.vizu import VizuVrep

VECT_C = [0.85, 0.356, 0.31, 0]
MARKER_C = [0.325, 0.46, 0.478, 0]
OBJ_C = [0.752, 0.16, 0.258, 0]

cfg = desc._deepcopy()
cfg.vrep.ppf         = 200
cfg.vrep.headless    = True
cfg.vrep.vglrun      = False
cfg.vrep.calibrdir   = '~/.dovecot/tttcal/'
#cfg.vrep.mac_folder  = '/Applications/VRep/vrep.app/Contents/MacOS/'
cfg.vrep.mac_folder  ='/Users/pfudal/Stuff/VREP/3.0.5/vrep.app/Contents/MacOS'
cfg.vrep.load        = True
cfg.sprims.prefilter = False
#cfg.logger.folder = '~/.dovecot/logger/'
cfg.logger.folder = '/Users/pfudal/Stuff/Fabien/dovecot/examples/tools/LOGS/'

def filter_data(datas):
    d = []
    for e in datas:
        if e is not None:
            d.append(e)
    return d

def load_file(filename, folder=None):
    if folder is None:
        folder, filename = os.path.split(filename)
    l = logger.Logger(folder=folder, filename=filename)
    return l.load()

def not_implemented(datas):
    print("Vrep plots for these data is not implemented yet.")

def start_com(datas):
    com = None
    if len(datas) > 0:
        for data in datas:
            if data != None:
                scene = data['datas']['scene']
                print(scene)
                break
        cfg.execute.scene.name = scene
    com = VizuVrep(cfg, calcheck=False)
    return com

def show_traj_data(datas):
    com = start_com(datas)
    for data in datas[0:1]:
        trajs = []
        move = data['datas']['object_sensors']
        vrep_traj = data['datas']['tip_sensors']
        col_XYZ = data['datas']['collide_data']
        for coord in vrep_traj:
            trajs.append(coord)
        if len(col_XYZ) >= 3:
            coordinates = []
            coordinates.append(col_XYZ[0])
            coordinates.append(col_XYZ[1])
            coordinates.append(col_XYZ[2])
            com.add_spheres_set(MARKER_C, 0.045, coordinates)

            #com.add_lines_set(MARKER_C, 2, trajs)
            com.add_curve(MARKER_C, 2, vrep_traj, 4)
            if len(move) >= 14:
                com.add_curve(VECT_C, 2, [move[0], move[1], move[2], move[-7], move[-6], move[-5]], 1)
                for i in range(0, len(move), 7 * 15):
                    com.add_spheres_set(OBJ_C, 0.045, [move[i], move[i+1], move[i+2]])
            com.update_current_color()
    com.draw(ppf=200)
    return data

def show_collide_data(datas):
    #com = start_com(datas)
    for data in datas:
        col_XYZ = data['datas']['collide_data']
        if len(col_XYZ) == 3:
            coordinates = []
            coordinates.append(col_XYZ[0])
            coordinates.append(col_XYZ[1])
            coordinates.append(col_XYZ[2])
            com.add_spheres_set(COLLIDE_COLOR, 0.045, coordinates)
            #com.add_points_set(COLLIDE_COLOR, 2, coordinates)
            com.update_current_color() # same color for each point
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
    if len(sys.argv) != 2:
        print("args1 = log file")
        exit(1)
    datas = sys.argv[1]

    folder = None
    if not os.path.isabs(datas):
        folder = cfg.logger.folder
    datas_datas = filter_data(load_file(datas, folder=folder))

    show_traj_data(datas_datas)

def main_2():
    if len(sys.argv) != 2: #3
        # print("usage : python {} <log name> --list".format(sys.argv[0]))
        print("usage : python {} <log name>".format(sys.argv[0]))
    else:
        fname = sys.argv[1]
        #option = sys.argv[2]

        folder = None
        if not os.path.isabs(fname):
            folder = cfg.logger.folder
        datas = filter_data(load_file(fname, folder=folder))

        # if option == "--list":
            # list_all_keyword(datas)
        show_traj_data(datas)
        # show_collide_data(datas)
        # elif option.startswith("--"):
        #     print("error : {} is not a valid option".format(option))
        #     print("usage : python {} <log name> --list".format(sys.argv[0]))
        # else:
        #     print("Showing vrep plot for \"{}\"".format(sys.argv[2]))
        #     try:
        #         dispatch[option](datas)
        #     except KeyError:
        #         print("{} is not a valid keyword.".format(option))

if __name__ == '__main__':
    main()
