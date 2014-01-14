import math

import env
from surrogates.vrepsim import vrepcom

n_steps = 500
pos   = [(0.1 * e) * math.pi / 180.0 for e in range(n_steps)]
speed = [(0.1 * e) * math.pi / 180.0 for e in range(n_steps)]

max_steps = 1000
trajectory = [[pos, speed]]*6

try:
    vcom = vrepcom.VrepCom(ppf=2000)
    for _ in range(10):
        vcom.run_simulation(trajectory, max_steps)

except Exception:
    import traceback
    traceback.print_exc()
finally:
    vcom.close()
