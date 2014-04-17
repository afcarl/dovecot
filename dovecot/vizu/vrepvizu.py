"""
    Class used to make Vrep print logged data
"""
from __future__ import print_function, division, absolute_import

import time
import os
import random

from ..vrepsim import vrepcom
from .. import ttts
import pyvrep

OBJECT_TYPE = {'point' : 0, 'line' : 1, 'sphere' : 2, 'curve' : 1}
OBJECT_SIZE = {'point' : 3, 'line' : 6, 'sphere' : 3, 'curve' : 3}
HEADER_SIZE = 7

SIM_PAUSED = pyvrep.constants.sim_simulation_paused

DEFAULT_TRANSPARENCY = 0

def sample_data(data, sample_level):
    """
        sampel data using the given sample level
    """
    if sample_level < 1:
        raise ValueError(sample_level)
    filtered_data = data[::min(sample_level, len(data))]
    filtered_data += [data[-1]]
    sampled_data = []
    for i in range(len(filtered_data) - 1):
        if filtered_data[i + 1] != filtered_data[i]:
            sampled_data.append(filtered_data[i])
            sampled_data.append(filtered_data[i + 1])
    return sampled_data

def sample_curve_coordinates(coordinates, sample_level):
    """
        Sample coordinates
    """
    if len(coordinates) % 3 != 0 or len(coordinates) < 6:
        raise ValueError("error coordinates length")
    x_s, y_s, z_s = [], [], []
    for i in range(int(len(coordinates) / 3)):
        x_s.append(coordinates[3 * i])
        y_s.append(coordinates[3 * i + 1])
        z_s.append(coordinates[3 * i + 2])
    xs_sampled = sample_data(x_s, sample_level)
    ys_sampled = sample_data(y_s, sample_level)
    zs_sampled = sample_data(z_s, sample_level)
    assert len(xs_sampled) == len(ys_sampled) == len(zs_sampled), \
        'Error in sampled data.'
    curve_coordinates = []
    for i in range(len(xs_sampled)):
        curve_coordinates.append(xs_sampled[i])
        curve_coordinates.append(ys_sampled[i])
        curve_coordinates.append(zs_sampled[i])
    return curve_coordinates

def get_random_color(transparency):
    random.seed(time.time())
    return [random.random(), random.random(), random.random(), transparency]

class VizuVrep(vrepcom.VRepCom):
    """
        This class connect itself to Vrep and print data
        using points, lines and curves
    """
    def __init__(self, cfg, verbose=False, calcheck=False):
        super(self.__class__, self).__init__(cfg, verbose=False, calcheck=False)
        self.data = [float(0)]
        self.current_color = get_random_color(DEFAULT_TRANSPARENCY)

    def load(self, script="vizu", calcheck=False):
        """
            Load a scene, set the script handle name to the given parameter
            and perform a calibration checking if asked
        """
        self.scene_name = '{}_{}'.format('vizu', self.cfg.sprims.scene)

        if calcheck:
            self.caldata = ttts.TTTCalibrationData(self.scene_name,
                                                   self.cfg.vrep.calibrdir)
            self.caldata.load()

        if not self.connected:
            if not self.vrep.connect_str(self.port):
                raise IOError("Unable to connect to vrep")
            self.connected = True

        scene_filepath = ttts.TTTFile(self.scene_name).filepath
        assert os.path.isfile(scene_filepath), \
            "scene file {} not found".format(scene_filepath)

        print("loading v-rep scene {}".format(scene_filepath))
        self.vrep.simLoadScene(scene_filepath)
        self.handle_script = self.vrep.simGetScriptHandle(script)

    def update_current_color(self, transparency=0):
        self.current_color = get_random_color(transparency)

    def _add_set(self, obj_type, color, size, coordinates):
        """
            Add a set ob object to draw
            coordinates : (x1, y1, z1, ...)
        """
        if color != None:
            if len(color) != 4:
                raise ValueError("Error in color components...")
        if len(coordinates) % OBJECT_SIZE[obj_type] != 0:
            raise ValueError("Error in coordinates : {} / {}".format(len(coordinates), OBJECT_SIZE[obj_type]))
        self.data[0] += 1.0
        self.data.append(float(HEADER_SIZE + len(coordinates)))
        self.data.append(float(OBJECT_TYPE[obj_type]))
        for comp in {not None:color, None:self.current_color}[color]:
            self.data.append(float(comp))
        self.data.append(float(size))
        self.data.append(float(len(coordinates)))
        for crdn in coordinates:
            self.data.append(float(crdn))

    def add_points_set(self, color, size, coordinates):
        """
            Add a set of points
            color = (r, g, b, a)
            size = s
            coordinates = (x, y, z, x, y, z, x, ...)
        """
        self._add_set('point', color, size, coordinates)

    def add_spheres_set(self, color, size, coordinates):
        """
            Add a set of spheres
            color = (r, g, b, a)
            size = s
            coordinates = (x, y, z, x, y, z, x, ...)
        """
        self._add_set('sphere', color, size, coordinates)

    def add_lines_set(self, color, size, coordinates):
        """
            Add a set of lines
            color = (r, g, b, a)
            size = s
            coordinates = (x00, y00, z00, x01, y01, z01,
                           x10, y10, z10, x11, y11, z11, etc)
        """
        self._add_set('line', color, size, coordinates)

    def add_curve(self, color, size, coordinates, sample_level):
        """
            Add a curve
            color = (r, g, b, a)
            size = s
            coordinates = (at least, on couple x,y,z
        """
        self._add_set('curve', color, size,
                      sample_curve_coordinates(coordinates, sample_level))

    def draw(self, keep_toy=True, ppf=200):
        """
            Draw data in Vrep then kill it
        """
        #print(self.data)
        self.vrep.simSetScriptSimulationParameterDouble(
                self.handle_script, "Keep_Toy", [{True:1, False:0}[keep_toy]])
        self.vrep.simSetScriptSimulationParameterDouble(
                self.handle_script, "Data", list(self.data))
        self.vrep.simSetSimulationPassesPerRenderingPass(ppf)
        self.vrep.simStartSimulation()
        wait = True
        while wait:
            time.sleep(0.0001) # probably useless; let's be defensive.
            if self.vrep.simGetSimulationState() == SIM_PAUSED:
                wait = False
        raw_input("Press Enter to stop Vrep...")
        self.vrep.simStopSimulation()

