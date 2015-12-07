## \file demoDynamicalSystems.py
## \author Freek Stulp
## \brief  Visualizes results of demoDynamicalSystems.cpp
## 
## \ingroup Demos
## \ingroup DynamicalSystems

import matplotlib.pyplot as plt
import numpy
import os, sys, subprocess


if __name__=='__main__':
    executable = "../../../bin/demoDynamicalSystems"
    
    if (not os.path.isfile(executable)):
        print ""
        print "ERROR: Executable '"+executable+"' does not exist."
        print "Please call 'make install' in the build directory first."
        print ""
        sys.exit(-1);
    
    # Call the executable with the directory to which results should be written
    directory = "/tmp/demoDynamicalSystems"
    subprocess.call([executable, directory])
    
