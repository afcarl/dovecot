"""
get list of usb devices:
    lsusb
get details about a device:
    udevadm info -a -n /dev/bus/usb/003/002
cycle device:
    sudo sh -c "echo 0 > /sys/bus/usb/devices/3-1.1/authorized"
    sudo sh -c "echo 1 > /sys/bus/usb/devices/3-1.1/authorized"
"""

import os

if os.uname()[0] == 'Linux':
    import pyudev

from toolbox import execute

def usb_syspath():
    context = pyudev.Context()
    return {device['ID_SERIAL_SHORT']: device.sys_path for device in context.list_devices(subsystem='usb', ID_VENDOR_ID='0403', ID_MODEL_ID='6001')}

def cycle_usb(stemcfg):
    execute.execute('sudo ~/cycle_usb.sh {}'.format(stemcfg.sysloc))

class StemCfg(object):

    def __init__(self, uid=None,
                       serial_id=None,
                       hostname=None,
                       optitrack_addr=None,
                       optitrack_side=None,
                       motorid_range=None,
                       calib_file=None,
                       model_file=None,
                       zero_pose=None,
                       angle_limits=None):
        self.uid = uid
        self.serial_id = serial_id

        self.optitrack_addr = optitrack_addr
        self.optitrack_side = optitrack_side

        self.motorid_range = motorid_range or (0, 253)
        self.calib_file = calib_file
        self.model_file = model_file

        self.zero_pose = zero_pose
        self.angle_limits = angle_limits

    def cycle_usb(self):
        if os.uname()[0] == 'Linux':
            import pyudev
            self.syspath = usb_syspath()[self.serial_id]
            self.sysloc  = os.path.basename(self.syspath)
            execute.execute('sudo ~/cycle_usb.sh {}'.format(self.sysloc), quiet=True)
        else:
            raise OSError("cycle_usb is not supported yet on your platform !")

stem0 = StemCfg(uid=0,
                serial_id='A8006BPa',
                hostname='optistem',
                optitrack_addr='239.255.42.99',
                optitrack_side='left',
                motorid_range=(1, 6),
                calib_file='calib0.data',
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150))

stem1 = StemCfg(uid=1,
                serial_id='A4008aCD',
                hostname='optistem',
                optitrack_addr='239.255.42.99',
                optitrack_side='right',
                motorid_range=(41, 46),
                calib_file='calib1.data',
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150))

stem2 = StemCfg(uid=2,
                serial_id='A4008apX',
                hostname='latistem',
                optitrack_addr='239.255.42.98',
                optitrack_side='left',
                motorid_range=(11, 16),
                calib_file='calib1.data',
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150))

stem3 = StemCfg(uid=3,
                serial_id='A9005MWF',
                hostname='latistem',
                optitrack_addr='239.255.42.98',
                optitrack_side='right',
                motorid_range=(50, 56),
                calib_file='calib1.data',
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150))

stems = [stem0, stem1, stem2, stem3]
