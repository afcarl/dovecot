import sys

import dotdot
import dovecot
from dovecot.ext import powerswitch


if len(sys.argv) >= 2:
    uid = int(sys.argv[1])
else:
    uid = dovecot.stem_uid()

powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6', load_config=True).set_off(uid)
