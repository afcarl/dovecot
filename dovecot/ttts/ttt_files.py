from __future__ import print_function, division, absolute_import
import os
import hashlib
import pickle

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
        self.name = name
        self.folder = folder
        ttt_file = TTTFile(name)
        self.ttt_filepath = ttt_file.filepath
        self.cal_filepath = cleanpath(os.path.join(self.folder, ttt_file.filename + '.cal'))

        self.md5            = None
        self.mass           = None
        self.position       = None
        self.position_world = None
        self.dimensions     = None
        self.dimensions_m   = None

    def populate(self, mass, position, dimensions, position_world, dimensions_m):
        self.md5 = md5sum(self.ttt_filepath)
        self.mass = mass
        self.position = position
        self.position_world = position_world
        self.dimensions = dimensions
        self.dimensions_m = dimensions_m

    def save(self):
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
        with open(self.cal_filepath, 'r') as f:
            caldata = pickle.load(f)
        self.md5 = md5sum(self.ttt_filepath)
        assert caldata.md5 == self.md5, "loaded scene calibration ({}) differs from scene ({})".format(self.cal_filepath, self.ttt_filepath)

        self.dimensions     = caldata.dimensions
        self.dimensions_m     = caldata.dimensions_m
        self.mass           = caldata.mass
        self.position       = caldata.position
        self.position_world = caldata.position_world

    def __repr__(self):
        s  = 'ttt_file: {}, md5: {}\n'.format(self.ttt_filepath, self.md5)
        s += 'cal_file: {}\n'.format(self.cal_filepath)
        s += 'mass: {}, pos: {}, world_pos:{}, dim: {}, dime_marker: {}\n'.format(self.mass, self.position, self.position_world, self.dimensions, self.dimensions_m)
        return s



