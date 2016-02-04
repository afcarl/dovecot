#!/usr/bin/env python
import os
import glob
import subprocess

from setuptools           import setup, find_packages
from setuptools.extension import Extension

import versioneer



VERSION = '3.1'

LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH', '').split(':')
INCLUDE_PATH = (os.environ.get('C_INCLUDE_PATH', '').split(':') +
			    os.environ.get('CPLUS_INCLUDE_PATH', '').split(':'))


def boost_libname(name):
	"""Find which boost library version exist on the system,
	between multi-threaded and not. If both exists, choose the
	non multi-threaded.
	"""
	for path in LD_LIBRARY_PATH + ['/usr/local/lib/']:
		if len(glob.glob(os.path.join(path, 'lib' + name + '.*'))) > 0:
			return '-l{}'.format(name)
		elif len(glob.glob(os.path.join(path, 'lib' + name + '-mt.*'))) > 0:
			return '-l{}-mt'.format(name)
	raise IOError("Library {} was not found".format(name))


def compile_args(packages):
	args = []
	for pkg in packages:
		p = subprocess.Popen('pkg-config {} --cflags'.format(pkg).split(), stdout=subprocess.PIPE)
		args += p.communicate()[0].decode('utf-8').split()
	return args

def link_args(packages):
	args = []
	for pkg in packages:
		p = subprocess.Popen('pkg-config {} --libs'.format(pkg).split(), stdout=subprocess.PIPE)
		args += p.communicate()[0].decode('utf-8').split()
	return args

cmdclass = versioneer.get_cmdclass()


try:
    from Cython.Build         import cythonize
    ext = 'pyx'
except ImportError:
	ext = 'cpp'

ext_modules = [
    Extension(
        name     = 'dovecot.ext.dynamics.fcl',
        language = 'c++',
        sources  = ['dovecot/ext/dynamics/fcl/fcl.' + ext,
                    'dovecot/ext/dynamics/fcl/_fcl.cpp'],

        include_dirs       = INCLUDE_PATH + ['/usr/local/include/'],
		library_dirs       = LD_LIBRARY_PATH + ['/usr/local/lib/'],
        extra_compile_args = compile_args(['fcl', 'ccd']) + ['-O3', '-std=c++0x'],
        extra_link_args    = (link_args(['fcl', 'ccd'])
		 					  + [boost_libname('boost_thread'), '-lboost_date_time', '-lboost_filesystem'])
    ),
    Extension(
        name     = 'dovecot.ext.pydmp',
        language = 'c++',
        sources  = ['dovecot/ext/pydmp/pydmp.' + ext,
                    'dovecot/ext/pydmp/_dmp.cpp'],

        include_dirs       = INCLUDE_PATH + ['/usr/local/include/'],
		library_dirs       = LD_LIBRARY_PATH + ['/usr/local/lib/'],
        extra_compile_args = ['-O3', '-std=c++0x'],
        extra_link_args    = ['-ldmp', '-lfunctionapproximators', '-ldynamicalsystems',
						      '-lboost_filesystem', '-lboost_serialization', '-lboost_system']
    )]

if ext == 'pyx':
    ext_modules = cythonize(ext_modules)



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
    install_requires = ['six', 'scicfg', 'environments', 'numpy', 'sympy'],
    ext_modules = ext_modules
)
