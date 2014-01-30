import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "surrogates",
    version = "1",
    author = "Fabien Benureau",
    author_email = "fabien.benureau@inria.fr",
    description = ("A simplistic robotic interface for different robotic simulation and hardware"),
    license = "Not Yet Decided.",
    keywords = "robots interface",
    url = "flowers.inria.fr",
    packages=['surrogates', 'surrogates.kinsim',
                            'surrogates.vrepsim',
                            'surrogates.prims',
                            'surrogates.stemsim', 'surrogates.stemsim.adjust',
                                                  'surrogates.stemsim.calibration',
                                                  'surrogates.stemsim.collider',
                                                  'surrogates.stemsim.stemcfg',
                                                  ],
    classifiers=[],
    package_data={'surrogates.vrepsim': ['surrogate.ttt'],
                  'surrogates.stemsim': ['ar.ttt'],
                  'surrogates.stemsim.collider'  : ['stem.smodel'],
                  'surrogates.stemsim.calibration' : ['calib0.data', 'calib1.data', 'calib2.data', 'calib3.data']},
)