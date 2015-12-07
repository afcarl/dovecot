from __future__ import print_function, division
import time
import sys

from pydyn import MotorSet

import dotdot
import dovecot
from dovecot.ext import powerswitch
from dovecot.ext.toolbox import gfx
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
#ms.zero_pose    = stem.zero_pose
#ms.angle_ranges = stem.angle_ranges

def observe_max_angles():
    max_angles = [[float('inf'), float('-inf')] for _ in ms.motors]
    start = time.time()
    while time.time()-start < 60.0:
        max_angles = [[min(lb, p), max(hb, p)] for (lb, hb), p in zip(max_angles, ms.pose)]

    print(', '.join(gfx.ppv(ma) for ma in max_angles))


ms.max_torque            = 100
ms.ccw_angle_limit       =  150
ms.cw_angle_limit        = -150
ms.ccw_compliance_margin = 0.3
ms.cw_compliance_margin  = 0.3
#ms.compliance_margines  = (1.0, 1.0)
ms.ccw_compliance_slope_bytes  = 32
ms.cw_compliance_slope_bytes   = 32
#ms.compliance_slopes    = (16, 16)
ms.return_delay_time     = 0
ms.status_return_level   = 1
ms.alarm_led_bytes       = 37
ms.alarm_shutdown_bytes  = 37

time.sleep(1.0)
