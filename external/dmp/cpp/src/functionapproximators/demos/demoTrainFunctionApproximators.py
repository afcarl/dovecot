## \file demoTrainFunctionApproximators.py
## \author Freek Stulp
## \brief  Visualizes results of demoTrainFunctionApproximators.cpp
## 
## \ingroup Demos
## \ingroup FunctionApproximators

import matplotlib.pyplot as plt
import os, sys, subprocess

# Include scripts for plotting
lib_path = os.path.abspath('../plotting')
sys.path.append(lib_path)
from plotData import plotDataFromDirectory
from plotLocallyWeightedLines import plotLocallyWeightedLinesFromDirectory

if __name__=='__main__':
    executable = "../../../bin/demoTrainFunctionApproximators"
    
    if (not os.path.isfile(executable)):
        print ""
        print "ERROR: Executable '"+executable+"' does not exist."
        print "Please call 'make install' in the build directory first."
        print ""
        sys.exit(-1);
    
    # Call the executable with the directory to which results should be written
    directory = "/tmp/demoTrainFunctionApproximators"
    subprocess.call([executable, directory])
    
    # Plot the results in each directory
    function_approximator_names = ["LWR","IRFRLS"]
    fig = plt.figure()
    subplot_number = 1;
    for name in function_approximator_names:
    
    
        ax = fig.add_subplot(1,len(function_approximator_names),subplot_number)
        subplot_number += 1;
    
        directory_fa = directory +"/"+ name
        plotDataFromDirectory(directory_fa,ax)
        if (name=="LWR"):
            plotLocallyWeightedLinesFromDirectory(directory_fa,ax)
        ax.set_title(name)
        ax.set_ylim(-1.0,1.5)
    
    ax.legend(['targets','predictions'])
    plt.show()
    

