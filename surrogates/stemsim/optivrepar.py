import time
import numpy as np
from surrogates.vrepsim import vrepcom
import env
from natnet import FrameBuffer
import treedict

class OptiVrepAR(object):
    def __init__(self, port=1984, verbose=True, ppf=200, scene="../stemsim/ar.ttt", script="marker"):
        self.ppf = ppf
        self.port = 1984
        self.verbose = verbose
        self.scene = scene
        self.script = script
        cfg = treedict.TreeDict()
        cfg.sensors.tip = False
        self.opivcom = vrepcom.OptiVrepCom(cfg, load=False, verbose=self.verbose, headless=False, vrep_folder=None, ppf=self.ppf)
        if not self.opivcom.connected:
            self.opivcom.load(self.scene, self.script)

    def execute(self, trackdata):
        return self.opivcom.run_trajectory(trackdata)

