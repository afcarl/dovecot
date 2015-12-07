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

from ...ext.toolbox import execute

def usb_syspath():
    import pyudev
    context = pyudev.Context()
    return {device['ID_SERIAL_SHORT']: device.sys_path for device in context.list_devices(subsystem='usb', ID_VENDOR_ID='0403', ID_MODEL_ID='6001')}

def cycle_usb(serial_id):
    if os.uname()[0] == 'Linux':
        syspath = usb_syspath()[serial_id]
        sysloc  = os.path.basename(syspath)
        execute.execute('sudo ~/cycle_usb.sh {}'.format(sysloc), print_cmd=False, print_output=False)
    else:
        raise OSError("cycle_usb is not supported yet on your platform !")

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
                       powerswitch_mac=None,
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
        self.powerswitch_mac = powerswitch_mac

    def cycle_usb(self):
        cycle_usb(self.serial_id)

    @property
    def angle_limits(self):
        return tuple((zp-ar_low-3.0, zp+ar_high+3.0) for zp, (ar_low, ar_high) in zip(self.zero_pose, self.angle_ranges))

angle_ranges = ((110.0,  110.0), (99.0, 99.0), (99.0, 99.0), (120.0, 120.0), (99.0, 99.0), (99.0, 99.0))

stem0 = StemCfg(uid=0,
                serial_id='A4008bke',
                hostname='optistem',
                optitrack_addr='239.255.42.94',
                optitrack_side='bottom.right',
                motorid_range=(9, 15),
                model_file='stem.smodel',
                zero_pose=(0, 0, 3, 5, 0, 0),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch_mac='00:13:f6:01:52:d6',
                powerswitch=0)

stem1 = StemCfg(uid=1,
                serial_id='A9005MWF',
                hostname='optistem',
                optitrack_addr='239.255.42.94',
                optitrack_side='upper.right',
                motorid_range=(9, 15),
                model_file='stem.smodel',
                zero_pose=(-2, 0, 3, 0, 2, 0),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch_mac='00:13:f6:01:52:d6',
                powerswitch=1)

stem2 = StemCfg(uid=2,
                serial_id='AH00R9U0',
                hostname='optistem',
                optitrack_addr='239.255.42.94',
                optitrack_side='bottom.left',
                motorid_range=(9, 15),
                model_file='stem.smodel',
                zero_pose=(-3, 0, 0, -3, 0, 0),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch_mac='00:13:f6:01:52:d6',
                powerswitch=2)

stem3 = StemCfg(uid=3,
                serial_id='A4012AJS',
                hostname='optistem',
                optitrack_addr='239.255.42.94',
                optitrack_side='upper.left',
                motorid_range=(9, 15),
                model_file='stem.smodel',
                zero_pose=(-1, 0, 0, 2, 0, 0),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch_mac='00:13:f6:01:52:d6',
                powerswitch=3)

# this is the fifth stem
stem4 = StemCfg(uid=4,
                serial_id='A4012AJS',
                hostname='optistem',
                optitrack_addr='239.255.42.94',
                optitrack_side='bottom.right',
                motorid_range=(9, 15),
                model_file='stem.smodel',
                zero_pose=(-2, 0, 0, -9, 0, 0),
                angle_ranges=angle_ranges,
                max_torque=100,
                powerswitch_mac='00:13:f6:01:52:d6',
                powerswitch=3)

# test stem
stem5 = StemCfg(uid=5,
                serial_id='A9005MWF',
                hostname='latistem',
                optitrack_addr='239.255.42.94',
                optitrack_side='right',
                motorid_range=(90, 96),
                model_file='stem.smodel',
                zero_pose=(0, 0, 0, 0, 0, 0),
                angle_ranges=angle_ranges,
                powerswitch_mac='00:13:f6:01:52:d6',
                powerswitch=3,
                max_torque=100)

stems = [stem0, stem1, stem2, stem3, stem4]
