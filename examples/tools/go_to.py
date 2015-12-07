from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import dotdot
import dovecot
from dovecot.ext import powerswitch
from dovecot.stemsim import stemcfg

uid = dovecot.stem_uid()

pose = [float(sys.argv[i+1]) for i in range(6)]

stem = stemcfg.stems[uid]
stem.cycle_usb()

ps = powerswitch.Eps4m(mac_address=stemcfg.stems[stem.uid].powerswitch_mac, load_config=True)
ps_port = stemcfg.stems[stem.uid].powerswitch
if ps.is_off(ps_port):
    ps.set_on(ps_port)
    time.sleep(1)
while ps.is_restarting(ps_port):
    time.sleep(1)

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, timeout=10, verbose=True)
ms.zero_pose = stem.zero_pose

ms.moving_speed = 100
ms.max_torque   = 100
ms.torque_limit = 100
ms.pose = pose

time.sleep(2.0)
print("pos: [{}]".format(', '.join('{:.1f}'.format(p) for p in ms.pose)))
