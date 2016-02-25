from __future__ import print_function, division
import time


def observe_max_angles(ms):
    max_angles = [[float('inf'), float('-inf')] for _ in ms.motors]
    start = time.time()
    while time.time()-start < 60.0:
        max_angles = [[min(lb, p), max(hb, p)] for (lb, hb), p in zip(max_angles, ms.pose)]

    print(max_angles)

def set_angle_limits(ms, angle_limits):
    angle_limits = [(50.9, 249.3), (50.9, 249.3), (50.9, 249.3), (50.9, 249.3), (50.9, 249.3), (50.9, 249.3)]

    for m, al in zip(ms.motors, angle_limits):
        if al is not None:
            m.angle_limits = al
    time.sleep(0.1) # change are taking effect

def print_angle_limits(ms):
    for m in ms.motors:
        print(m.angle_limits)

def print_compliance_margins(ms):
    for m in ms.motors:
        print(m.compliance_margins)

def print_compliance_slopes(ms):
    for m in ms.motors:
        print(m.compliance_slopes)
#        print(m.compliance_slopes_raw)


def set_compliance_margins(ms, v):
    for m in ms.motors:
        m.compliance_margins = (v, v)
    time.sleep(0.1) # change are taking effect

def set_compliance_slopes(ms, v):
    for m in ms.motors:
        m.compliance_slopes = (v, v)
    time.sleep(0.1) # change are taking effect

def set_max_torque(ms, v):
    for m in ms.motors:
        m.max_torque = v
    time.sleep(0.1) # change are taking effect

def set_status_return_level(ms, v):
    for m in ms.motors:
        m.status_return_level = 1
    time.sleep(0.1)


def complete_setup(ms, angle_limits):
    set_angle_limits(ms, angle_limits)
    set_compliance_margins(ms, 1.0)
    set_compliance_slopes(ms, 16)
    set_max_torque(ms, 100)
