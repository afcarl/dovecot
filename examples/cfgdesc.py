import numbers
import forest

desc = forest.Tree()
desc._strict(True)

# FIXME should not not be in a branch
desc._isinstance('partial_mvt', bool)



    # Hardware stem config
desc._branch('stem')
# FIXME meaning ?
desc._isinstance('stem.dt', numbers.Real)
# FIXME diff between the two ?
desc._isinstance('stem.verbose_com', bool)

desc._isinstance('stem.verbose_dyn', bool)



    # V-REP config
desc._branch('vrep')
desc._isinstance('vrep.scene', str)

# pass of the physic engine per frame (max 200)
desc._isinstance('vrep.ppf', numbers.Integral)

desc._isinstance('vrep.headless', bool)

desc._isinstance('vrep.vglrun', bool)

desc._isinstance('vrep.calibrdir', str)



    # Sensory primitives
desc._branch('sprims')

# the scene to load in vrep #FIXME diff between vrep.scene ?
# if equal to 'cube_center', experiments are pure simulation, then 'vrep_cube_center.ttt' is loaded
# else, 'ar_cube_center.ttt' is loaded
desc._isinstance('sprims.scene', str)

# the names of the sensory primitives whose sensory feedback is computed
desc._isinstance('sprims.names', collections.Iterable)

# do we track the tip during sim ?
desc._isinstance('sprims.tip', bool)

# recast every sensory dimension between 0 and 1 ?
desc._isinstance('sprims.uniformize', bool)

# use collision detection to avoid running non-colliding episodes ?
desc._isinstance('sprims.prefilter', bool)



    # Motor primitives
desc._branch('mprim')

# name of the motor primitive
desc._isinstance('mprim.name', str)

# the number of position (and possibly velocity) orders executed
desc.mprim.motor_steps = 500

# defines when the simulation is finished
desc.mprim.max_steps   = 500

# uniformize motor orders dimension between 0 and 1 ?
desc.mprim.uniformze   = False

# how many basis for the dmp ?
desc.mprim.n_basis     = 2

# the maximum speed of the motors # FIXME units ?
desc.mprim.max_speed   = 1.0

# when does the dmp trajectory end ?
desc.mprim.end_time    = 1.15

# starting position of the stem
desc.mprim.init_states   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# target position of the stem
desc.mprim.target_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
