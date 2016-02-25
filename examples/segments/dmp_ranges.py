import env
import random
import numpy as np
from dovecot.prims import dmp as pydmp

res = 5

x_max = float('-inf')
x_min = float('inf')

xd_max = float('-inf')
xd_min = float('inf')

bins = [0 for _ in range(200)]


n = 2
for i in  range(1000):
    #print center, offset, center, width
    dmp = pydmp.DMP(1)
    dmp.dmp.set_initial_state([0.0])
    dmp.dmp.set_attractor_state([0.0])
    dmp.dmp.set_timesteps(500, 0.0, 5.0)
    dmp.lwr_meta_params(n)
    dmp.lwr_model_params(slopes = [random.uniform(-400, 400) for a in range(n)], offsets = [random.uniform(-400, 400) for b in range(n)], centers = [1.67, 3.33], widths = [random.uniform(0.05, 1.0) for c in range(n)])
    ts, xs, xds = dmp.trajectory()

    for x in xs:
        bins[int(10*x)+100] += 1

    x_max = max(x_max, max(xs))
    x_min = min(x_min, min(xs))

    xd_max = max(xd_max, max(xds))
    xd_min = min(xd_min, min(xds))


bins[100] = 0

print('max  x: {:5.2f}'.format(x_max))
print('min  x: {:5.2f}'.format(x_min))

print('max xd: {:5.2f}'.format(xd_max))
print('min xd: {:5.2f}'.format(xd_min))

print(bins)

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def plot(bins_numbers, bins_values):

    fig = matplotlib.figure.Figure()
    fig.canvas = FigureCanvas(fig)

    xs_color  = (250/255.0,105/255.0,  0/255.0)
    xds_color = (105/255.0,210/255.0,231/255.0)

    subplot = fig.add_subplot(1, 1, 1, axisbg=(1.0, 1.0, 1.0))
    subplot.plot(bins_numbers, bins_values,  color=xs_color)
    for tl in subplot.get_yticklabels():
        tl.set_color(xs_color)
    subplot.set_ylabel('bins', color=xs_color)


    filename = './bins.png'
    fig.savefig(filename, dpi=300, format='png',
                          facecolor=(1.0, 1.0, 1.0))
    print('graph saved in {}'.format(filename))

plot(range(-100, 100), bins)
