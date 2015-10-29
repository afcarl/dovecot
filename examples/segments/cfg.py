import forest

import dotdot
from dovecot import desc
from dovecot import objdesc

cfg0 = desc._copy(deep=True)

cfg0.execute.partial_mvt = True
cfg0.execute.prefilter   = False

cfg0.execute.check_self_collisions = False #True
cfg0.execute.is_simulation	       = True

cfg0.execute.kin.force  = 1.0

cfg0.execute.hard.verbose_com  = True
cfg0.execute.hard.verbose_dyn  = True
cfg0.execute.hard.powerswitch  = True

cfg0.execute.simu.headless     = False
cfg0.execute.simu.vglrun       = False
cfg0.execute.simu.ppf          = 200
cfg0.execute.simu.load         = True
cfg0.execute.simu.mac_folder   = '/Applications/VRep/vrep.app/Contents/MacOS/' # only for mac

cfg0.execute.scene.name        = 'vanilla'
cfg0.execute.scene.arena.name  = 'arena20x20x10'
# cfg0.execute.scene.objects.ball45 = objdesc._deepcopy()
# cfg0.execute.scene.objects.ball45.mass    = 0.050
# cfg0.execute.scene.objects.ball45.pos     = (-60.0, 0.0, None)
# cfg0.execute.scene.objects.ball45.tracked = True
cfg0.execute.scene.objects.cube45 = objdesc._deepcopy()
cfg0.execute.scene.objects.cube45.mass    = 0.050
cfg0.execute.scene.objects.cube45.pos     = (-60.0, 0.0, None)
cfg0.execute.scene.objects.cube45.tracked = True

cfg0.sprims.names      = ['push']
cfg0.sprims.tip        = False
cfg0.sprims.uniformize = False
cfg0.sprims.max_force  = 3000

cfg0.mprims.name        = 'dmp_sharedwidth'
cfg0.mprims.dt          = 0.020
cfg0.mprims.target_end  = 250
cfg0.mprims.traj_end    = 500
cfg0.mprims.sim_end     = 1000
cfg0.mprims.uniformize  = False
cfg0.mprims.n_basis     = 2
cfg0.mprims.max_speed   = 50

cfg0.mprims.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg0.mprims.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cfg0.mprims.angle_ranges  = ((110.0,  110.0), (99.0, 99.0), (99.0, 99.0), (120.0, 120.0), (99.0, 99.0), (99.0, 99.0))

cfg0.execute.simu.calibrdir = '~/.dovecot/tttcal/'

cfg1 = cfg0._copy(deep=True)
"""#TODO can't create new leaf 'scene' in a strict tree without a type or validation function declared"""
#cfg1.vrep.scene       = 'vrep_cylinder.ttt'
cfg1.sprims.names      = ['rollspin']
cfg1.execute.scene.name = 'cylinder'
