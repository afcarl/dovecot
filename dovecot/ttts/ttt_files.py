from __future__ import print_function, division, absolute_import
import os
import hashlib
import pickle

from toolbox import gfx

def cleanpath(path):
    return os.path.normpath(os.path.abspath(os.path.expanduser(path)))

def md5sum(filename, blocksize=65536):
    md5hash = hashlib.md5()
    with open(filename, "r") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            md5hash.update(block)
    return md5hash.hexdigest()


class TTTFile(object):
    def __init__(self, name):
        """
        :param name:   the name of the scene (ie. 'ar_center_cube')
                       the name of the ttt file will be deduced by adding '.ttt',
                       (ie. 'ar_center_cube.ttt')
        :param folder: the folder with the calibration file.
        """
        self.name = name
        self.folder = cleanpath(os.path.join(os.path.dirname(__file__), 'files'))
        self.filename = self.name + '.ttt'
        self.filepath = cleanpath(os.path.join(self.folder, self.filename))


class TTTCalibrationData(object):
    """Hold the calibration data of a scene"""

    def __init__(self, name, folder):
        """
        :param name:   the name of the scene (ie. 'ar_center_cube')
                       the name of the ttt file will be deduced by adding '.ttt',
                       and the name of the calibration file will add '.ttt.cal',
                       (ie. 'ar_center_cube.ttt.cal')
        :param folder: the folder with the calibration file.
        """
        self.name   = name
        self.folder = folder
        ttt_file    = TTTFile(name)
        self.ttt_filepath = ttt_file.filepath
        self.cal_filepath = cleanpath(os.path.join(self.folder, ttt_file.filename + '.cal'))

        self.md5        = None
        self.objects    = {}
        self.marker_dim = None

        self.verbose    = True

    def pos_r(self, p):
        return tuple(np.array(p) + np.array(self.robot_pos_w))

    def populate(self, objects, robot_pos_w, marker_dim):
        self.md5         = md5sum(self.ttt_filepath)
        self.objects     = objects
        self.robot_pos_w = robot_pos_w
        self.marker_dim  = marker_dim

    def save(self):
        print(self.objects)
        if self.verbose:
            print('{}cal: {}saving calibration data {}{}'.format(gfx.grey, gfx.cyan, self.cal_filepath, gfx.end))
        with open(self.cal_filepath, 'w+') as f:
            pickle.dump(self, f)

    def load(self):
        """\
        Load the calibration file

        Verify that the md5 on file match the md5 of the .ttt file.
        Retrieve the dimensions, mass and position for the .cal file.
        """
        if not os.path.isfile(self.ttt_filepath):
            raise IOError("error: scene file {} not found".format(self.ttt_filepath))
        if not os.path.isfile(self.cal_filepath):
            raise IOError("error: calibration file {} not found".format(self.cal_filepath))
        if self.verbose:
            print('{}cal: {}loading calibration data {}{}'.format(gfx.grey, gfx.cyan, self.cal_filepath, gfx.end))

        with open(self.cal_filepath, 'r') as f:
            caldata = pickle.load(f)
        self.md5 = md5sum(self.ttt_filepath)
        assert caldata.md5 == self.md5, "{}cal: {}loaded scene calibration ({}:{}) differs from scene ({}:{}){}".format(gfx.grey, gfx.red, self.cal_filepath, caldata.md5, self.ttt_filepath, self.md5, gfx.end)

        self.objects     = caldata.objects
        self.marker_dim  = caldata.marker_dim
        self.robot_pos_w = caldata.robot_pos_w

    def __repr__(self):
        s  = 'ttt_file: {}, md5: {}\n'.format(self.ttt_filepath, self.md5)
        s += 'cal_file: {}\n'.format(self.cal_filepath)
        # s += 'mass: {}, pos: {}, world_pos:{}, dim: {}, dime_marker: {}\n'.format(self.mass, self.position, self.position_world, self.dimensions, self.dimensions_m)
        return s


class VRepObject(object):

    def __init__(self, name):
        """
            :param pos:   position relative to the robot
            :param pos_w: absolute position
        """
        self.name = name

    def setup(self, pos, pos_w, dim, mass):
        self.pos   = pos
        self.pos_w = pos_w
        self.dim   = dim
        self.mass  = mass

    def load(self, com, base_h):
        self.handle = com._vrep_get_handle(self.name)
        self.pos    = tuple(100*p for p in com.vrep.simGetObjectPosition(self.handle, base_h))
        self.pos_w  = tuple(100*p for p in com.vrep.simGetObjectPosition(self.handle, -1))
        self.dim, self.mass = self.object_properties(com.vrep, self.handle)

    def actual_pos(cls, start_pos, cfg_pos):
        """Return the position of the object after it has been moved by configuration defined postion"""
        assert all(p_s is not None for p_s in start_pos)
        return tuple(p_c if p_c is not None else p_s for p_c, p_s in zip(cfg_pos, start_pos))

    @classmethod
    def object_properties(cls, vrep, handle):
        min_x = vrep.simGetObjectFloatParameter(handle,   21)[0] * 100
        max_x = vrep.simGetObjectFloatParameter(handle,   24)[0] * 100
        min_y = vrep.simGetObjectFloatParameter(handle,   22)[0] * 100
        max_y = vrep.simGetObjectFloatParameter(handle,   25)[0] * 100
        min_z = vrep.simGetObjectFloatParameter(handle,   23)[0] * 100
        max_z = vrep.simGetObjectFloatParameter(handle,   26)[0] * 100
        mass  = vrep.simGetObjectFloatParameter(handle, 3005)[0]

        dims = (max_x - min_x, max_y - min_y, max_z - min_z)

        return dims, mass

