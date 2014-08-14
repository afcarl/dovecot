from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
import powerswitch
import dovecot
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


def go_to(ms, pose, margin=10.0, timeout=5.0):
    start = time.time()
    ms.pose = pose

    while (time.time() - start < timeout and
           max(abs(p - tg) for p, tg in zip(ms.pose, pose) if tg is not None) > 10):
        time.sleep(0.1)


if max(abs(p-0.0) for p in ms.pose[3:]) > 10.0:

    ms.moving_speed = [  100,   100,   100, None, None, None]
    ms.torque_limit = [   50,    50,    50, None, None, None]
    ms.compliant    = [False, False, False, True, True, True]
    time.sleep(0.1)

    go_to(ms, [0.0, 0.0, 0.0, None, None, None])

ms.moving_speed = 100
ms.torque_limit =  50
ms.compliant    = False
time.sleep(0.1)

go_to(ms, [0.0]*6)
