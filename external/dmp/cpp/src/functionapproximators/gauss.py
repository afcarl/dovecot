import sys

import math
def g(mu, sigma, x):
    return math.exp(-(mu-x)**2/(2*sigma*sigma))

print(g(0, 0.1, float(sys.argv[1])))

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def plot_g(sigma):
    fig = matplotlib.figure.Figure()
    fig.canvas = FigureCanvas(fig)


    ts = [0.01*i for i in range(100)]
    xs = [g(0, sigma, t) for t in ts]

    subplot = fig.add_subplot(1, 1, 1, axisbg=(1.0, 1.0, 1.0))
    subplot.plot(ts, xs)

    fig.savefig('guass{}.png'.format(sigma), dpi=300, format='png', 
                       facecolor=(1.0, 1.0, 1.0))

plot_g(0.02)