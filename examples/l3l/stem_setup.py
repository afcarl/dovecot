from __future__ import print_function, division
import time
from pydyn import MotorSet

ms = MotorSet()

def observe_max_angles():
    max_angles = [[float('inf'), float('-inf')] for _ in ms.motors]
    start = time.time()
    while time.time()-start < 60.0:
        max_angles = [[min(lb, p), max(hb, p)] for (lb, hb), p in zip(max_angles, ms.pose)]

    print(max_angles)

def set_angle_limits():
    angle_limits = [(50.9, 249.0), (50.9, 249.0), (50.9, 249.0), (50.9, 249.0), (50.9, 249.0), (50.9, 249.0)]

    for m, al in zip(ms.motors, angle_limits):
        if al is not None:
            m.angle_limits = al
    time.sleep(0.1) # change are taking effect

def print_angle_limits():
    for m in ms.motors:
        print(m.angle_limits)

def print_compliance_margins():
    for m in ms.motors:
        print(m.compliance_margins)

def print_compliance_slopes():
    for m in ms.motors:
        print(m.compliance_slopes)
#        print(m.compliance_slopes_raw)


def set_compliance_margins(v):
    for m in ms.motors:
        m.compliance_margins = (v, v)
    time.sleep(0.1) # change are taking effect

def set_compliance_slopes(v):
    for m in ms.motors:
        m.compliance_slopes = (v, v)
    time.sleep(0.1) # change are taking effect


set_angle_limits()
print_angle_limits()

set_compliance_margins(1.0)
#set_compliance_slopes(16)
print_compliance_margins()
#print_compliance_slopes()
