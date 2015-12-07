from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import dotdot
import dovecot
from dovecot.ext import powerswitch
from dovecot.stemsim import stemcfg

if len(sys.argv) >= 2:
    uid = int(sys.argv[1])
else:
    uid = dovecot.stem_uid()

stem = stemcfg.stems[uid]
stem.cycle_usb()

ps = powerswitch.Eps4m(mac_address=stemcfg.stems[stem.uid].powerswitch_mac, load_config=True)
ps_port = stemcfg.stems[stem.uid].powerswitch
if ps.is_off(ps_port):
    ps.set_on(ps_port)
    time.sleep(1)
while ps.is_restarting(ps_port):
    time.sleep(1)

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)
ms.zero_pose = stem.zero_pose
ms.angle_limits = stem.angle_limits

ms.compliant = False
time.sleep(0.1)

ms.moving_speed    = 100
ms.torque_limit = 50

rest_pose = [5.3, 96.3, -97.8, 0.6, -46.5, -10]
ms.pose = rest_pose

while max(abs(p - tg) for p, tg in zip(ms.pose, rest_pose)) > 10:
    time.sleep(0.1)

ms.moving_speed = 20
ms.torque_limit = 5

start_time = time.time()
while max(abs(p - tg) for p, tg in zip(ms.pose, rest_pose)) > 2.0 and time.time()-start_time < 1.0:
    time.sleep(0.05)

ms.compliant = True
time.sleep(0.3)
print(ms.compliant)
# for m in ms.motors:
#     m.request_read('torque_enable')
# time.sleep(0.3)
# print(ms.compliant)
