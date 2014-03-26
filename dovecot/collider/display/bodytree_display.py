import random

import pyglet.gl as gl

from . import cube_display

red = (1.0, 0.0, 0.0)

class PlacedCube(object):

    def __init__(self, body, color = None):
        self.cube = cube_display.Cube(body.size)
        self.body = body
        self.color = color
        if self.color is None:
            self.color = (0, 1, 0)
            #self.color = (random.random(), random.random(), random.random())
        self.collides = False

    def draw(self):
        T = self.body.T

        mT = T.flatten('F').tolist()[0]

        mT = (gl.GLfloat * len(mT))(*mT)  # FIXME there is prob a better way...
        gl.glMultMatrixf(mT)
        if self.collides:
            gl.glColor3f(*red)
        else:
            gl.glColor3f(*self.color)
        self.cube.draw()

class BodyTreeCubes(object):

    def __init__(self, bodytree):
        self.bt = bodytree
        self.bodies = self.bt.bodies()
        self.cubes = [PlacedCube(body) for body in self.bodies]
        self.cubes_map = {c.body.meta: c for c in self.cubes}
        cube_display.drawables.append(self)

        cube_display.g_tbcam.rot_quat = [-0.281, 0.831, 0.449, -0.166]
        cube_display.g_tbcam.cam_eye  = [0.0, 0.0, -538.0]

    def setup(self):
        cube_display.setup()

    def green(self):
        for c in self.cubes:
            c.collides = False

    def add_update_function(self, f):
        cube_display.updates_f.append(f)

    def draw(self):
        for cube in self.cubes:
            gl.glPushMatrix()
            cube.draw()
            gl.glPopMatrix()

    def run(self):
        cube_display.run()
