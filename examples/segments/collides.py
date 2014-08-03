from __future__ import print_function, division
import sys, time

import pydyn

import env
from dovecot.stemsim.collider import collider
from dovecot.stemsim import stemcfg

scfg = stemcfg.stems[int(sys.argv[1])]
stem = pydyn.MotorSet(serial_id=scfg.serial_id, motor_range=scfg.motorid_range, verbose=True)
stem.zero_pose = scfg.zero_pose

while True:
    if len(collider.collide(stem.pose)) > 0:
        sys.stdout.write('\a')
        print('collision !  ', end='\r')
    else:
        print('no collision.', end='\r')
    sys.stdout.flush()
    time.sleep(0.01)
