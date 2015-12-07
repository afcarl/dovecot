from distutils.core import setup, Extension

# define the name of the extension to use
extension_name    = 'pydmp'
extension_version = '1.0'

# define the directories to search for include files
# to get this to work, you may need to include the path
# to your boost installation. Mine was in
# '/usr/local/include', hence the corresponding entry.
include_dirs = [ '/usr/local/include', '/home/optistem/prefix/include/']

# define the library directories to include any extra
# libraries that may be needed.  The boost::python
# library for me was located in '/usr/local/lib'
library_dirs = [ '/usr/local/lib', '/home/optistem/prefix/lib/' ]

# define the libraries to link with the boost python library
libraries = [ 'boost_python', 'boost_system', 'boost_serialization', 'boost_filesystem', 'python2.7', 'dmp', 'functionapproximators', 'dynamicalsystems' ]

# define the source files for the extension
source_files = [ 'main.cpp', 'src/dmp/demos/pydmp.cpp', 'GenericList.cpp']

# create the extension and add it to the python distribution
setup(       name=extension_name,
          version=extension_version,
      ext_modules=[Extension(extension_name, source_files,
                             include_dirs=include_dirs,
                             library_dirs=library_dirs,
                             libraries=libraries,
                             language="c++",
                             extra_compile_args=['-std=c++0x', '-fPIC'],
                             #extra_link_args=['-lboost_python', '-lboost_system', '-lboost_serialization', '-lboost_filesystem']
                            )]
     )
