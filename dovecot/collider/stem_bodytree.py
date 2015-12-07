from __future__ import print_function, division, absolute_import
import os

from ..ext.dynamics.fwdkin import bodytree, smodel

sm = smodel.SymbolicModel.from_file(os.path.abspath(os.path.join(__file__, '..')) + '/' + 'stem.smodel')
bt = bodytree.BodyTree(sm)


def attach(degree, size, trans, meta='', groups=tuple()):
    sf = bodytree.SubFrameT(*trans)
    sf.attach(bodytree.Box(size, meta=meta, groups=groups))
    bt.attach(sf, degree)


world_group = 0
ref1_group  = 1
ref2_group  = 2
ref3_group  = 3
ref4_group  = 4
ref5_group  = 4
ref6_group  = 4
tip_group   = 7


# Ref0
#attach(0, (1000, 1000,  70), (-465, 0, -25), meta='table', groups=[world_group])
attach(0, ( 100, 1000, 100), (-25,   0, -25), meta='beam', groups=[world_group])
#attach(0, (  55.,   75, 165), (22/2,  75/2 + 30, -165/2 + 25), meta='clawL', groups=[world_group])
#attach(0, (  55.003,   75, 165), (22/2, -75/2 - 30, -165/2 + 25), meta='clawR', groups=[world_group])
attach(0, (  20,   20,  15), (0,  70,   7), meta='boltL', groups=[world_group])
attach(0, (  20,   20,  15), (0, -70,   7), meta='boltR', groups=[world_group])
attach(0, (  40,   60,  45), (0,   0,  22), meta='motor0_bind', groups=[world_group])

# Ref1
attach(1, (61.105, 40.2, 41), (22 - 61.1/2, 0, 0),  meta='motor0',          groups=[world_group, ref1_group])
attach(1, (80.0, 100.0, 75.0), (22 - 61.1/2, 0, 0), meta='motor0_safezone', groups=[world_group, ref1_group])

# Ref2
attach(2, (34.006, 45, 60), (0,  13, 0), meta='horn0', groups=[ref2_group, world_group])

# Ref3
attach(3, (112.007, 51, 60), (-42.5, 0, 0), meta='motorhorn1', groups=[ref2_group, ref3_group, world_group]) # FIXME should not collide wit world_group

# Ref4
attach(4, ( 40.008, 60, 80), (0, 0, 25), meta='motorhorn2', groups=[ref4_group, ref3_group, ref1_group]) # FIXME should not collide wit ref1_group

# Ref5
attach(5, ( 90.009, 40, 50), (-90/2+12, 0, 0), meta='motorhorn3', groups=[ref4_group, ref3_group, ref5_group])

# Ref6
attach(6, ( 80.010, 40, 50), (-80/2+12, 0, 0), meta='motorhorn4', groups=[ref6_group, ref5_group])

# Ref6
attach(7, ( 60.011, 40, 50), (-67, 0, 0), meta='motor5', groups=[ref6_group, tip_group])

# Tip
attach(7, (40.012,  5,  5), (-20, 0, 0), meta='marker_stem', groups=[tip_group])
attach(7, (22.013, 22, 22), (  0, 0, 0), meta='marker', groups=[tip_group])

bt.update((0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
