import env
import numpy as np
from surrogates.prims import dmp as pydmp

res = 5

x_max = float('-inf')
x_min = float('inf')

xd_max = float('-inf')
xd_min = float('inf')

for slope in np.linspace(-400.0, 400.0, num=res):
    for offset in np.linspace(-400.0, 400.0, num=res):
        for center in np.linspace(0.0, 1.0, num=res):
            for width in np.linspace(0.0, 1.0, num=res):
                #print center, offset, center, width
                dmp = pydmp.DMP()
                dmp.dmp.set_timesteps(120, 0.0, 2.0)
                dmp.lwr_meta_params(1)
                dmp.lwr_model_params(slopes = [slope], offsets = [offset], centers = [center], widths = [width])
                ts, xs, xds = dmp.trajectory()
                
                x_max = max(x_max, max(xs))
                x_min = min(x_min, min(xs))

                xd_max = max(xd_max, max(xds))
                xd_min = min(xd_min, min(xds))

print('max  x: {:5.2f}'.format(x_max))
print('min  x: {:5.2f}'.format(x_min))

print('max xd: {:5.2f}'.format(xd_max))
print('min xd: {:5.2f}'.format(xd_min))
