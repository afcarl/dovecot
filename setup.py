from setuptools import setup, find_packages

import versioneer

VERSION = '3.1'

setup(
    name         = 'dovecot',
    version      = VERSION,
    cmdclass     = versioneer.get_cmdclass(),
    author       = 'Fabien Benureau, Paul Fudal',
    author_email = 'fabien.benureau@gmail.com',
    description  = 'A python library to drive the hardware and simulation experiment of the author PhD thesis',
    license      = 'Open Science License',
    keywords     = 'science experiment hardware simulation robots',
    url          = 'https://github.com/humm/dovecot',
    packages     = find_packages(),
    classifiers  = [],
    package_data = {'dovecot.ttts.files'    : ['vanilla.ttt', 'script_robot.lua'],
                    'dovecot.collider'      : ['stem.smodel'],
                    'dovecot.calibration.triocal' : ['calib0.data',
                                                     'calib1.data',
                                                     'calib2.data',
                                                     'calib3.data']}, # FIXME should be dynamic
    install_requires = ['scicfg', 'environments', 'numpy', 'sympy'],
)
