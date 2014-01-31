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
                       model_file=None,
                       zero_pose=None,
                       angle_ranges=None,
                       max_torque=None,
                       powerswitch=None):
        assert uid is not None

        self.uid = uid
        self.serial_id = serial_id

        self.optitrack_addr = optitrack_addr
        self.optitrack_side = optitrack_side

        self.calib_file = 'calib{}.data'.format(uid)
        self.vrep_capture_file = 'vrep_capture{}.data'.format(uid)
        self.opti_capture_file = 'opti_capture{}.data'.format(uid)
        self.model_file = model_file

        self.motorid_range = motorid_range or (0, 253)
        self.zero_pose = zero_pose
        self.angle_ranges = angle_ranges
        self.max_torque = max_torque
        self.powerswitch = powerswitch

    def cycle_usb(self):
        if os.uname()[0] == 'Linux':
            import pyudev
            self.syspath = usb_syspath()[self.serial_id]
            self.sysloc  = os.path.basename(self.syspath)
            execute.execute('sudo ~/cycle_usb.sh {}'.format(self.sysloc), quiet=True)
        else:
            raise OSError("cycle_usb is not supported yet on your platform !")

    @property
    def angle_limits(self):
        return tuple((zp-ar_low-3.0, zp+ar_high+3.0) for zp, (ar_low, ar_high) in zip(self.zero_pose, self.angle_ranges))

angle_ranges = ((110.0,  110.0), (99.0, 99.0), (99.0, 99.0), (120.0, 120.0), (99.0, 99.0), (99.0, 99.0))

stem0 = StemCfg(uid=0,
                serial_id='A8006BPa',
                hostname='optistem',
                optitrack_addr='239.255.42.99',
                optitrack_side='left',
                motorid_range=(1, 6),
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch=1)

stem1 = StemCfg(uid=1,
                serial_id='A4008aCD',
                hostname='optistem',
                optitrack_addr='239.255.42.99',
                optitrack_side='right',
                motorid_range=(41, 46),
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch=2)

stem2 = StemCfg(uid=2,
                serial_id='A4008apX',
                hostname='latistem',
                optitrack_addr='239.255.42.98',
                optitrack_side='right',
                motorid_range=(11, 16),
                model_file='stem.smodel',
                zero_pose=(173.0, 149.0, 149.0, 176.0, 149.6, 129.9),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch=3)

stem3 = StemCfg(uid=3,
                serial_id='A4008bke',
                hostname='latistem',
                optitrack_addr='239.255.42.98',
                optitrack_side='left',
                motorid_range=(51, 56),
                model_file='stem.smodel',
                zero_pose=(172, 150, 150, 172, 150, 150),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch=4)

stems = [stem0, stem1, stem2, stem3]
