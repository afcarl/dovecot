import time
import sys

import pydyn.dynamixel as dyn
import natnet

ctrl = dyn.create_controller(verbose = True, motor_range = [0, 6], timeout = 0.05)

# init pose
def init_pose():

    for m in ctrl.motors:
        m.compliant = False
        m.torque = 50
        m.speed = 100
        m.position = 150

    ctrl.motors[0].position = 170
    ctrl.motors[3].position = 170
    ctrl.motors[5].position = 100

    time.sleep(2)

ref_point = (-0.1036, 0.2461, 0.1383)

def dist(a, b):
    assert len(a) == len(b)
    return sum(abs(a_i - b_i)**2 for a_i, b_i in zip(a, b))

def tip_pos_idx():
    frame = nnclient.receive_frame()
    data = frame.unpack_data()
    sets = data['markersets']

    for s in sets:
        if s[0] == 'Rigid Body 1':
            d_ref   = [dist(ref_point, p) for p in s[1]]
            min_ref = min(d_ref)
            return d_ref.index(min_ref)

    assert False

def tip_pos(m_idx):
    frame = nnclient.receive_frame()
    data = frame.unpack_data()
    sets = data['markersets']

    for k, s in enumerate(sets):
        if s[0] == 'Rigid Body 1':
            return s[1][m_idx]


def track():
    pass

if __name__ == "__main__":
    #init_pose()

    nnclient = natnet.NatNetClient()

    m_idx = tip_pos_idx()
    while True:
        pos = tip_pos(m_idx)
        if pos is not None:
            print('{}\r'.format(', '.join('{:7.4f}'.format(e) for e in pos))),
            sys.stdout.flush()
        time.sleep(0.01)