from mpl_toolkits.mplot3d.axes3d import Axes3D
import numpy                                                                  
import matplotlib.pyplot as plt                                               
import os, sys

lib_path = os.path.abspath('../plotting')
sys.path.append(lib_path)

from plotData import getDataDimFromDirectory
from plotData import plotDataFromDirectory
from plotLocallyWeightedLines import plotLocallyWeightedLinesFromDirectory


def plotFunctionApproximatorTrainingFromDirectory(directory,ax):
    """zzz."""
    plotLocallyWeightedLinesFromDirectory(directory,ax)
    plotDataFromDirectory(directory,ax)
    
        
    

if __name__=='__main__':
    """Pass a directory argument, read inputs, targets and predictions from that directory, and plot."""

    if (len(sys.argv)==2):
        directory = str(sys.argv[1])
    else:
        print '\nUsage: '+sys.argv[0]+' <directory>    (data is read from directory)\n';
        sys.exit()
    
  
    fig = plt.figure() 
    if (getDataDimFromDirectory(directory)==1):
      ax = fig.gca()
    else:
      ax = Axes3D(fig)
      
    plotFunctionApproximatorTrainingFromDirectory(directory,ax)
    plt.show()


