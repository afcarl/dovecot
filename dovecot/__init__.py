from __future__ import absolute_import, division, print_function

from .cfgdesc import desc
from .cfgdesc import objdesc

from .vrepsim.sim_env import SimulationEnvironment
from .kinsim.kin_env import KinEnvironment
from .kinsim.kin_display import KinDisplay

try:
    from .stemsim.hard_env import HardwareEnvironment
    from .stemsim.hard_env import stem_uid
except ImportError:
    pass

from . import vrepsim
from . import prims

from ._version import get_versions
__version__ = get_versions()["version"]
__commit__ = get_versions()["full-revisionid"]
__dirty__ = get_versions()["dirty"]
del get_versions
