from __future__ import print_function

import sys
import random
import time

import scicfg
from toolbox import gfx

import dotdot
from dovecot import objdesc
from dovecot.vrepsim import sim_env
from cfg import cfg0

from environments import tools


cfg0.sprims.names      = ['push']

cfg0.execute.simu.ppf              = 5
cfg0.execute.simu.headless         = False
cfg0.execute.simu.calibr_check     = False
cfg0.execute.prefilter             = True
cfg0.execute.check_self_collisions = False

cfg0.mprims.n_basis                = 3
cfg0.sprims.max_force              = 10000

cfg0.execute.scene.name        = 'vanilla'
cfg0.execute.scene.objects.cube45.mass = 0.050
cfg0.execute.scene.objects.cube45.pos  = (-60.0, 0.0, None)

cfg0.execute.scene.objects.ball45 = objdesc._deepcopy()
cfg0.execute.scene.objects.ball45.pos     = (+60.0, 180.0, None)
cfg0.execute.scene.objects.ball45.mass    = 0.500
cfg0.execute.scene.objects.ball45.tracked = False

# cfg0.execute.scene.objects.y_objwall         = objdesc._deepcopy()
# cfg0.execute.scene.objects.y_objwall.pos     = (0.0, -30.0, None)
# cfg0.execute.scene.objects.y_objwall.mass    = 0.500
# cfg0.execute.scene.objects.y_objwall.tracked = False

total = 1
if len(sys.argv) >= 2:
    total = int(sys.argv[1])


def memory_usage():
    import resource
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem


vrepb = sim_env.SimulationEnvironment(cfg0)

cols = 0
col_orders = []

random.seed(0)

hard_col = []
start = time.time()


# import pickle
# with open('hard_col.m_signals', 'r') as f:
#     m_signals = pickle.load(f)
# for i, m_signal in enumerate(m_signals):

for i in range(total):
    start_order = time.time()

    # if i == 100 or i == total-1:
    #     import pdb; pdb.set_trace()
    m_signal = tools.random_signal(vrepb.m_channels)
    meta = {}
    feedback = vrepb.execute(m_signal, meta=meta)
    if 'raw_sensors' in meta['log']:
        max_force = -1.0
        salient_contacts = meta['log']['raw_sensors']['salient_contacts']
        if salient_contacts['max'] is not None:
            max_force = salient_contacts['max'].force_norm_sq
        #max_force = max([-1.0] + [c.force_norm_sq for c in meta['log']['raw_sensors']['contacts']])
        print('max_force_sq: {} N'.format(max_force))
        if max_force > 10000.0:
            hard_col.append(m_signal)
            print(tools.to_vector(m_signal, vrepb.m_channels))
            print('{}{}{}'.format(gfx.green, tools.to_vector(feedback['s_signal'], vrepb.s_channels), gfx.end))
    s_vector = tools.to_vector(feedback['s_signal'], vrepb.s_channels)
    if s_vector[2] != 0.0:
        cols += 1
        col_orders.append(m_signal)
        print()
#    print('{}({})/{}'.format(i+1, cols, total), end='\r')
    sys.stdout.flush()
    #print(' '.join('{:5.2f}'.format(e) for e in effect))
    dur = time.time()-start_order
    print('{:04d}: {:.2f} MiB'.format(i, memory_usage()))
    print('      {:4.2f}s for this order)'.format(dur))


dur = time.time()-start
print('\nran for {}s ({:4.2f}s per order)'.format(int(dur), dur/total))
print('collisions : {}/{} ({:5.2f}%)'.format(cols, total, 100.0*cols/total))

import pickle
with open('hard_col.m_signals', 'w') as f:
    pickle.dump(hard_col, f)
raw_input()

#print('\ncolliding order:')
#print(col_orders)
