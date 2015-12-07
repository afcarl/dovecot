import pydmp

def memory_usage():
    import resource, sys
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem


for i in range(101):
    if i % 10 == 0:
        print('{}: {:.2f} MiB'.format(i, memory_usage()))
    for j in range(6):
        dmp = pydmp.PyDMP(1)
        dmp.set_lwr_meta_parameters(1, 1, 0.1)
        dmp.set_lwr_model_parameters([0.2], [1], [-100], [-100])
        dmp.set_initial_state([0])
        dmp.set_attractor_state([1.0])
        dmp.set_timesteps(500, 0.0, 1.0)
        dmp.generate_trajectory()

