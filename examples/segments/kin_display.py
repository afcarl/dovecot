from __future__ import print_function

import random

from environments import tools

import dotdot
from dovecot import KinDisplay

from cfg import cfg0


random.seed(0)

env = KinDisplay(cfg0)

m_signal = tools.random_signal(env.m_channels)
m_signal = {'slope0.1': 181.14479646325424, 'slope0.0': -68.46193962353374, 'offset4.0': -320.1722208063401, 'offset4.1': 157.3431183449925, 'offset5.1': 329.83394057807436, 'offset5.0': 234.61018700774264, 'slope4.1': -316.03494800617983, 'slope4.0': 119.88979086700294, 'width0': 0.07844771156742526, 'width1': 0.05483708100616313, 'offset3.1': 32.3450392227864, 'slope2.1': -277.54651569030165, 'slope2.0': -179.01303137182535, 'slope3.0': 84.94097475144986, 'slope3.1': -23.464723964847963, 'offset2.0': -251.01864318151596, 'offset2.1': -299.71125525742906, 'offset1.1': -273.0973722433321, 'offset1.0': -386.56948959861586, 'slope1.0': 10.713937120223363, 'slope1.1': -193.80197954927985, 'offset0.0': -183.06945065478376, 'offset0.1': -33.88587230578412, 'offset3.0': -308.3726865498285, 'slope5.0': 102.92252280430756, 'slope5.1': 152.0191201895134}
feedback = env.execute(m_signal, meta={})


env.close()
