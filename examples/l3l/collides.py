from __future__ import print_function, division
import sys, time

import pydyn

import env
from surrogates.stemsim import collider

stem = pydyn.MotorSet(verbose=True)

while True:
    if len(collider.collide(stem.pose)) > 0:
        print('collision !  ', end='\r')
    else:
        print('no collision.', end='\r')
    time.sleep(0.01)
    sys.stdout.flush()