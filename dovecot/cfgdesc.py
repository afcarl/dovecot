import collections
import numbers

import forest

desc = forest.Tree()
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



    # Sensory primitives
desc._branch('sprims')

# the scene to load in vrep
# if equal to 'cube_center', experiments are pure simulation, then 'vrep_cube_center.ttt' is loaded
# else, 'ar_cube_center.ttt' is loaded
desc._isinstance('sprims.scene', str)

# the names of the sensory primitives whose sensory feedback is computed
desc._isinstance('sprims.names', collections.Iterable)

# do we track the tip during sim ?
desc._isinstance('sprims.tip', bool)

# recast every sensory dimension between 0 and 1 ?
desc._isinstance('sprims.uniformize', bool)



 	# Motor primitives
desc._branch('mprim')

# name of the motor primitive
desc._isinstance('mprim.name', str)

# the number of position (and possibly velocity) orders executed
desc._isinstance('mprim.motor_steps', numbers.Integral)

# the temporal resolution of the motor trajectory, in s
desc._isinstance('mprim.dt', numbers.Real)

# defines when the simulation is finished
desc._isinstance('mprim.max_steps', numbers.Integral)

# uniformize motor orders dimension between 0 and 1 ?
desc._isinstance('mprim.uniformize', bool)

# how many basis for the dmp ?
desc._isinstance('mprim.n_basis', numbers.Integral)

# the maximum speed of the motors # FIXME units ?
desc._isinstance('mprim.max_speed', numbers.Real)

# when does the dmp trajectory end ?
desc._isinstance('mprim.end_time', numbers.Real)

# starting position of the stem
desc._isinstance('mprim.init_states', collections.Iterable)

# target position of the stem
desc._isinstance('mprim.target_states', collections.Iterable)

desc._describe('mprim.angle_ranges', instanceof=collections.Iterable,
               docstring='The range of the angles of the joints around the zero position the motor primitives bounds its values into')

