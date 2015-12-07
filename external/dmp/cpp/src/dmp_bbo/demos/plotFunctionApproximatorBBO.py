import sys
import numpy                                                                    
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
import os
import matplotlib.pyplot as pl
import time
from matplotlib import animation

def plotEvolutionaryOptimization(n_updates,directory,ax):

    if (n_updates==0):
      n_updates += 1;

    first_targets = np.loadtxt(directory+"/targets.txt")
    ax.plot(np.linspace(0,1,len(first_targets)),first_targets,'-',color='b',lw=2,label='imitation (before optimization)');
    activations_normalized = np.loadtxt(directory+"/activations_normalized.txt")
    ax.plot(np.linspace(0,1,len(activations_normalized)),activations_normalized,'-',color='g',lw=0.5);    
    
    #################################
    # Visualize the rollouts 
    cur_directory = '%s/update%05d' % (directory, n_updates)
    cost_vars = np.loadtxt(cur_directory+"/cost_vars.txt")
    
    
    n_targets = len(cost_vars[0])/2
    targets = cost_vars[0,n_targets:]
    ax.plot(np.linspace(0,1,len(targets)),targets,'-',color='k',lw=2,label='target for optimization');
    lines = ax.plot(np.linspace(0,1,n_targets),cost_vars[:,0:n_targets].T);
    plt.setp(lines, linewidth=0.5)    
    
    #for kk in range(len(cost_vars)):
    #    predictions = cost_vars[kk,0:n_targets]
    #    print range(len(predictions))
    #    linelist[kk].set_data(range(len(predictions)),predictions);

# See if input directory was passed
if (len(sys.argv)==2):
  directory = str(sys.argv[1])
else:
  print '\nUsage: '+sys.argv[0]+' <directory>\n';
  sys.exit()

n_updates = 0;
dir_exists = True;
while (dir_exists):
  n_updates+=1
  cur_directory = '%s/update%05d' % (directory, n_updates)
  dir_exists = os.path.isdir(cur_directory)

n_updates-=1

fig = plt.figure(1,figsize=(12, 4))
n_subplots = 6;
updates_to_plot = linspace(1,n_updates,n_subplots)
print updates_to_plot
for i_subplot in range(n_subplots):
  if (i_subplot==0):
    ax = fig.add_subplot(1,n_subplots,i_subplot+1)
    ax1 = ax
  else:
    ax = fig.add_subplot(1,n_subplots,i_subplot+1,sharey=ax1)
    
  plotEvolutionaryOptimization(round(updates_to_plot[i_subplot]),directory,ax)
  ax.set_title('Update='+str(int(round(updates_to_plot[i_subplot]))))
  ax.set_xlabel('input')
  ax.set_ylabel('output')
    
#anim = animation.FuncAnimation(fig, plotEvolutionaryOptimization, init_func=init, frames=n_updates, fargs=(directory,), interval=100, blit=True)

plt.legend()
plt.show()

