import collections
import numbers

import environments


desc = environments.Environment.defcfg._deepcopy()
desc._strict(True)


    # Execution parameters
desc._branch('execute')

# if True, execute in simulation, else hardware
desc._isinstance('execute.is_simulation', bool)

# if True, self-collisions movements are allowed (and truncated)
desc._isinstance('execute.partial_mvt', bool)

# if True, self-collisions movements are forbidden (and truncated)
desc._isinstance('execute.check_self_collisions', bool)

# if True, self-collisions movements are allowed (and truncated)
desc._isinstance('execute.prefilter', bool)


    # Kinematic Surrogate parameters
desc._branch('execute.kin')

# the stem number
desc._isinstance('execute.kin.force', numbers.Real)


    # Hardware parameters
desc._branch('execute.hard')

# the stem number
desc._isinstance('execute.hard.uid', numbers.Integral)

# if True, control powerswitch during experiment
desc._isinstance('execute.hard.powerswitch', bool)

# FIXME diff between the two ?
desc._isinstance('execute.hard.verbose_com', bool)

desc._isinstance('execute.hard.verbose_dyn', bool)


    # Simulation parameters
desc._branch('execute.simu')

# will run with xfvb if True
desc._describe('execute.simu.verbose', instanceof=bool, default=False)

# do we load vrep or not ?
desc._isinstance('execute.simu.load', bool)

# pass of the physic engine per frame (max 200)
desc._isinstance('execute.simu.ppf', numbers.Integral)

# will run with xfvb if True
desc._isinstance('execute.simu.headless', bool)

# obsolete ?
desc._describe('execute.simu.vglrun', instanceof=bool, default=False)

# the location of the calibration folder
desc._isinstance('execute.simu.calibrdir', str)

# on mac, we need to know where vrep is
desc._isinstance('execute.simu.mac_folder', str)

# # the position (x, y, z) of the toy # NOT IMPLEMENTED YET
# desc._isinstance('execute.simu.toy_pos', collections.Iterable)


    # Scene Configuration
desc._branch('execute.scene')
desc._branch('execute.scene.object')

# name of the scene
desc._describe('execute.scene.name', instanceof=str)

# name of the object to track
desc._describe('execute.scene.object.name', instanceof=str)

# x, y, z - if some dimension must be inchanged, set to None.
desc._describe('execute.scene.object.pos', instanceof=collections.Iterable)

# mass of the object - set to None to leave to default.
desc._describe('execute.scene.object.mass', instanceof=(None.__class__, numbers.Real))


    # Sensory primitives
desc._branch('sprims')

# the names of the sensory primitives whose sensory feedback is computed
desc._isinstance('sprims.names', collections.Iterable)

# do we track the tip during sim ?
desc._isinstance('sprims.tip', bool)

# recast every sensory dimension between 0 and 1 ?
desc._isinstance('sprims.uniformize', bool)


 	# Motor primitives
desc._branch('mprims')

# name of the motor primitive
desc._describe('mprims.name', instanceof=str)

# temporal resolution of the trajectory and simulation step in seconds
desc._describe('mprims.dt', instanceof=numbers.Real)

# lengths of the trajectory
desc._describe('mprims.traj_end', instanceof=numbers.Integral)

# when the target should be reached during the trajectory
desc._describe('mprims.target_end', instanceof=numbers.Integral)

# when to stop the simulation
desc._describe('mprims.sim_end', instanceof=numbers.Integral)

# uniformize motor orders dimension between 0 and 1 ?
desc._describe('mprims.uniformize', instanceof=bool, default=True)

# number of basis functions for the dmp
desc._describe('mprims.n_basis', instanceof=numbers.Integral)

# the maximum speed of the motors in degree/seconds
desc._describe('mprims.max_speed', instanceof=numbers.Real)

# starting position of the stem
desc._describe('mprims.init_states', instanceof=collections.Iterable)

# target position of the stem
desc._describe('mprims.target_states', instanceof=collections.Iterable)

desc._describe('mprims.angle_ranges', instanceof=collections.Iterable,
               docstring='The range of the angles of the joints around the zero position the motor primitives bounds its values into')

