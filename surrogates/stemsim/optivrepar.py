import time

import numpy as np
import treedict

from natnet import FrameBuffer

from ..vrepsim import vrepcom
from ..vrepsim import objscene


class OptiVrepAR(object):
    def __init__(self, cfg, port=1984, verbose=True, ppf=200, script="marker"):
        self.ppf = ppf
        self.port = 1984
        self.verbose = verbose
        print(cfg.makeReport())

        self.scene = objscene.scenes[cfg.sprims.scene].filename
        self.script = script
        self.opivcom = vrepcom.OptiVrepCom(cfg, load=False, verbose=self.verbose, vrep_folder=None, ppf=self.ppf)
        if not self.opivcom.connected:
            self.opivcom.load(self.scene, self.script)

    def execute(self, trackdata):
        return self.opivcom.run_trajectory(trackdata)

    def close(self):
        self.opivcom.close()
