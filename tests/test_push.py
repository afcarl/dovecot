from __future__ import print_function, division, absolute_import
import unittest
import random
import math

import numpy as np

import env
from dovecot.prims.s_push import Push

class TestPush(unittest.TestCase):

    def test_push(self):
        p = Push(None)

        context = {'x_bounds': (-3.0, 3.0),
                   'y_bounds': (-3.0, 3.0),
                   'z_bounds': ( 1.4, 3.3)}
        p.process_context(context)

        ts = p.create_testset(50)
        print('({})'.format(', '.join('({})'.format(', '.join('{:+6.4f}'.format(t_i) for t_i in t)) for t in ts)))

if __name__ == '__main__':
    unittest.main()
