"""
Computing sensory primitives from raw data.
"""
from __future__ import print_function, division, absolute_import
import math


sprims = {}

def create_sprim(name, cfg):
    sensory_class = sprims[name]
    sensory_prim = sensory_class(cfg)
    return sensory_prim
