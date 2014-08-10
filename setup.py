import os
from distutils.core import setup

setup(
    name         = 'dovecot',
    version      = '2.0',
    author       = 'Fabien Benureau, Paul Fudal',
    author_email = 'fabien.benureau@inria.fr',
    description  = ('A python library to drive the hardware and simulation experiment of the author PhD thesis'),
    license      = 'Open Science',
    keywords     = 'science experiment hardware simulation robots',
    url          = 'flowers.inria.fr',
    packages = ['dovecot',
                'dovecot.vizu',
                'dovecot.prims',
                'dovecot.ttts',
                'dovecot.ttts.files',
                'dovecot.kinsim',
                'dovecot.vrepsim',
                'dovecot.stemsim',
                'dovecot.stemsim',
                'dovecot.stemsim.stemcfg',
                'dovecot.collider',
                'dovecot.calibration',
                'dovecot.calibration.triocal',
                'dovecot.calibration.tttcal'
               ],
    classifiers = [],
    package_data = {'dovecot.ttts.files'    : ['vanilla.ttt',
                                               'vanilla_rightwall.ttt',
                                               'calibrate.ttt'
                                               ],
                    'dovecot.collider'      : ['stem.smodel'],
                    'dovecot.calibration.triocal' : ['calib0.data',
                                                     'calib1.data',
                                                     'calib2.data',
                                                     'calib3.data']}, # FIXME should be dynamic
)
