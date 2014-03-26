#!/usr/bin/env python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

'''Displays a rotating torus using OpenGL.

This example demonstrates:

 * Using a display list
 * Fixed-pipeline lighting

'''

from math import pi, sin, cos

from pyglet.gl import *
from pyglet.window import key, mouse
import pyglet

from . import trackball_camera

try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4,
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)

@window.event
def on_resize(width, height):
    # Override the default on_resize handler to create a 3D projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 10000.)
    glMatrixMode(GL_MODELVIEW)
    g_tbcam.update_modelview()
    return pyglet.event.EVENT_HANDLED

def update(dt):
    for update_f in updates_f:
        update_f()

pyglet.clock.schedule(update)

drawables = []
updates_f = []

g_tbcam  = trackball_camera.TrackballCamera(40.0)
g_width  = 800
g_height = 600

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def norm1(x,maxx):
    """given x within [0,maxx], scale to a range [-1,1]."""
    return (2.0 * x - float(maxx)) / float(maxx)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        g_tbcam.mouse_roll(
            norm1(x, g_width),
            norm1(y,g_height),
            False)
    elif button == mouse.RIGHT:
        g_tbcam.mouse_zoom(
            norm1(10*x, g_width),
            norm1(10*y,g_height),
            False)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & mouse.LEFT:
        g_tbcam.mouse_roll(
            norm1(x,g_width),
            norm1(y,g_height))
    elif buttons & mouse.RIGHT:
        g_tbcam.mouse_zoom(
            norm1(10*x,g_width),
            norm1(10*y,g_height))

# @window.event
# def on_key_release(symbol, modifiers):
#     if symbol == key.UP


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    for drawable in drawables:
        glPushMatrix()
        drawable.draw()
        glPopMatrix()

def setup():
    # One-time GL setup
    glClearColor(1, 1, 1, 1)
    glColor3f(0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    #glEnable(GL_LIGHTING)
    #glEnable(GL_LIGHT0)
    #glEnable(GL_LIGHT1)

    # Define a simple function to create ctypes arrays of floats:
    def vec(*args):
        return (GLfloat * len(args))(*args)

    #glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    #glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    #glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    #glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    #glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    #glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

    #glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))

    #glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
    #glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    #glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

class Cube(object):
    def __init__(self, size):
        cube_normals = [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0,  0.0],
                        [0.0, -1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, -1.0]]
        cube_vertices_idx = [[3, 2, 1, 0], [7, 6, 2, 3], [4, 5, 6, 7],
                             [0, 1, 5, 4], [1, 2, 6, 5], [3, 0, 4, 7]];
        cube_vertices = self.create_vertices(size)
        # for c in cube_vertices:
        #     print c

        normals = []
        vertices = []
        for i in range(6):
            normals.append(cube_normals[i])
            vertices.append([cube_vertices[cube_vertices_idx[i][0]],
                             cube_vertices[cube_vertices_idx[i][1]],
                             cube_vertices[cube_vertices_idx[i][2]],
                             cube_vertices[cube_vertices_idx[i][3]]])

        # Create ctypes arrays of the lists
        #vertices = (GLfloat * len(vertices))(*vertices)
        #normals = (GLfloat * len(normals))(*normals)


        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        glBegin(GL_QUADS);
        for i in range(6):
            glNormal3f(*normals[i])
            for j in range(4):
                glVertex3f(*vertices[i][j])
        glEnd();
        glEndList()

    def create_vertices(self, size):
        a, b, c = size
        a, b, c = a/2, b/2, c/2
        v = [[0.0, 0.0, 0.0] for i in range(8)]
        v[0][0] = v[1][0] = v[2][0] = v[3][0] = -a
        v[4][0] = v[5][0] = v[6][0] = v[7][0] =  a
        v[0][1] = v[1][1] = v[4][1] = v[5][1] = -b
        v[2][1] = v[3][1] = v[6][1] = v[7][1] =  b
        v[0][2] = v[3][2] = v[4][2] = v[7][2] =  c
        v[1][2] = v[2][2] = v[5][2] = v[6][2] = -c
        return v

    def draw(self):
        glCallList(self.list)

def run():
    pyglet.app.run()
