import os
from distutils.core import setup

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
                            'surrogates.vrepsim', 'surrogates.vrepsim.objscene',
                            'surrogates.prims',
                            'surrogates.stemsim', 'surrogates.stemsim.adjust',
                                                  'surrogates.stemsim.calibration',
                                                  'surrogates.stemsim.collider',
                                                  'surrogates.stemsim.stemcfg',
                                                  ],
    classifiers=[],
    package_data={'surrogates.vrepsim.objscene': ['vrep_center_cube.ttt', 'vrep_calibrate.ttt', 'vrep_center_sphere.ttt', 'vrep_other_cube.ttt', 'vrep_cylinder.ttt', 'vrep_center_cylinder.ttt',
                                                  'ar.ttt', 'ar_center_cube.ttt', 'ar_center_sphere.ttt', 'ar_cylinder.ttt', 'ar_other_cube.ttt', 'ar_center_cylinder.ttt'],
                  'surrogates.stemsim.collider'  : ['stem.smodel'],
                  'surrogates.stemsim.calibration' : ['calib0.data', 'calib1.data', 'calib2.data', 'calib3.data']},
)