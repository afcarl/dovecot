from __future__ import print_function, division, absolute_import
import unittest

import scicfg

from dovecot.collider import maycollide

class TestMayCollide(unittest.TestCase):

    def test_maycollide(self):
        os_cube = objscene.scenes['cube']

        cfg = scicfg.SciConfig({'execute.kin.force': 10.0})
        cf = maycollide.CollisionFilter(cfg, os_cube.object_pos, os_cube.object_geoms, 11)

        print(cf.tip((0.0,)*6))

if __name__ == '__main__':
    unittest.main()
