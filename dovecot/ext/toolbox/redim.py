
def transform(v, hpc_origin, hpc_target):
    """Transform a vector v, from a given hypercube to the other, using appropriate translation and scaling."""
    assert len(v) == len(hpc_origin) == len(hpc_target)
    return tuple(((v_i - a)/(b - a)*(B - A) + A) for v_i, (a, b), (A, B) in zip(v, hpc_origin, hpc_target))

