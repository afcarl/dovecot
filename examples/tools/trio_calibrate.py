from __future__ import print_function, division
import sys
import time

import env
from dovecot.stemsim import stemcfg
from dovecot.calibration import triocal
import powerswitch

stem = stemcfg.stems[int(sys.argv[1])]
stem.cycle_usb()

ps = powerswitch.Eps4m(mac_address=stemcfg.stems[stem.uid].powerswitch_mac, load_config=True)
ps_port = stemcfg.stems[stem.uid].powerswitch
if ps.is_off(ps_port):
    ps.set_on(ps_port)
    time.sleep(1)
while ps.is_restarting(ps_port):
    time.sleep(1)

triocal.calibrate(stem, cached_opti=False, cached_vrep=False)
