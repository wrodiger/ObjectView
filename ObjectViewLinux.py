#!/usr/bin/python3
'''
		ObjectView for Python 3 (Mac os Python 3 version)
		
		Copyright (c) 2017 William K. Rodiger

		This code will render a wire frame object within the
		bounds of the defined window. The object file format is
		the same as ObjectView for Windows (.ov) files, with the 
		exception of the "_" character removed from all parameter
		names. Converted to Python using the fantastic Pythonista 
		IDE on Apple iOS.
		
		Pythonista version (Pythonista canvas) - 12/14/2017
		Mac version (tkinter) - 1/13/2018
		
'''
import math
#import canvas
from tkinter import Tk, Canvas

#
# setup constants
#

DIMS = 4
master = Tk()
master.withdraw()


#
#	class Objectv:
#
# Objectv contains data structures and methods for storing
# and manipulating an object. Paint() will output object with
# current view transformation
#
class Objectv(object):
    # method used in constructor
    def unit_diagonal(self, a):
        for i in range(DIMS):
            for j in range(DIMS):
                if i == j:
                    a[i][j] = 1.0
                else:
                    a[i][j] = 0.0

    # constructor
    def __init__(self, input_file):
        self.view = [[0.0] * 4 for i in range(25)]
        self.vert = [[0] * 3 for i in range(25)]
        self.face = [[0] * 8 for i in range(15)]
        self.edgenum = [0 for i in range(15)]
        self.rotx_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.rotx_tm)
        self.roty_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.roty_tm)
        self.rotz_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.rotz_tm)
        self.scale_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.scale_tm)
        self.trans_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.trans_tm)
        self.persp_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.persp_tm)
        self.view_tm = [[0.0] * DIMS for i in range(DIMS)]
        self.unit_diagonal(self.view_tm)
        self.xinc = self.yinc = self.zinc = 0.0
        self.frames = 0
        self.root = Tk()
        self.root.title("ObjectView for Python 3")
        self.canvas = Canvas(self.root, width=512, height=512, bg='black')
        self.canvas.pack()

        with open(input_file, "r") as object_file:
            self.name = object_file.readline().split()[0]
            object_file.readline()  # blank
            self.vertnum = int(object_file.readline().split()[1])
            self.facenum = int(object_file.readline().split()[1])
            self.scale = float(object_file.readline().split()[1])
            self.persp = 1 == int(object_file.readline().split()[1])
            self.d = float(object_file.readline().split()[1])
            self.s = float(object_file.readline().split()[1])
            self.xe = float(object_file.readline().split()[1])
            self.ye = float(object_file.readline().split()[1])
            self.ze = float(object_file.readline().split()[1])
            self.xt = float(object_file.readline().split()[1])
            self.yt = float(object_file.readline().split()[1])
            self.zt = float(object_file.readline().split()[1])
            self.x_inc = float(object_file.readline().split()[1])
            self.y_inc = float(object_file.readline().split()[1])
            self.z_inc = float(object_file.readline().split()[1])
            object_file.readline()  # blank
            object_file.readline()  # vertices
            for i in range(self.vertnum):
                self.vert[i][0:2] = object_file.readline().split()
                self.vert[i][3] = 1
            object_file.readline()  # blank
            object_file.readline()  # facenum
            for i in range(self.facenum):
                temp_line = object_file.readline().split()
                self.edgenum[i] = int(temp_line[0])
                # temp_line[0] contains number of vert in face
                for j in range(int(temp_line[0])):
                    self.face[i][j] = int(temp_line[j + 1])

    #
    #  Create an array of 25 float[4] arrays.
    #

    def init_array(self):
        return [[0 for col in range(4)] for row in range(25)]

    #
    #	Make a transformation matrix given the displacements.
    #

    def trans(self, dx, dy, dz, tm):
        tm[3][0] = dx
        tm[3][1] = dy
        tm[3][2] = dz

    #
    #	Scale the matrix.
    #

    def scaleit(self, sx, sy, sz, sm):
        sm[0][0] = sx
        sm[1][1] = sy
        sm[2][2] = sz

    #
    #	This procedure will set up the perspective matrix.
    #

    def perspect(self, s, d, m):
        p = d / s
        m[0][0] = p  # perspective equations
        m[1][1] = p

    #
    #	Make rotation matrices for rotations about the x, y and
    #	z axis and origin.
    #

    def rotx(self, th, rm):
        rm[1][1] = math.cos(th)  # cast float
        rm[2][2] = rm[1][1]
        rm[2][1] = math.sin(th)
        rm[1][2] = -rm[2][1]

    def roty(self, th, rm):
        rm[0][0] = math.cos(th)  # cast float
        rm[2][2] = rm[0][0]
        rm[0][2] = math.sin(th)
        rm[2][0] = -rm[0][2]

    def rotz(self, th, rm):
        rm[0][0] = math.cos(th)  # cast float
        rm[1][1] = rm[0][0]
        rm[1][0] = math.sin(th)
        rm[0][1] = -rm[1][0]

    #
    #	This procedure is for multiplying 4x4 matrices a and b together
    #	leaving the result as matrix c.
    #

    def am4x4(self, a, b, c):
        temp = [0.0 for i in range(DIMS)]
        for i in range(DIMS):
            for k in range(DIMS):
                temp[k] = a[i][k]  # save row
            for j in range(DIMS):
                r = 0.0  # use r instead of c[i,j] for efficiency
                for k in range(DIMS):
                    r += temp[k] * float(b[k][j])
                c[i][j] = r

    #
    # Matrix multiplication function to obtain a transformed point
    #	coordinate matrix c from the original point coordinate matrix
    #	a and the compound transformation matrix b. The matrix dimension
    # is d x DIMS.
    #

    def am20x4(self, b, c):
        for i in range(self.vertnum):
            for j in range(DIMS):
                r = 0.0  # use r instead of c[i,j] for efficiency
                for k in range(DIMS):
                    r += float(self.vert[i][k]) * float(b[k][j])
                c[i][j] = r

    #
    #	Applies transformation for auto rotation
    #

    def rotate(self):
        self.xinc += self.x_inc
        self.yinc += self.y_inc
        self.zinc += self.z_inc

    #
    # Objectv.paint()
    #
    #	Build the transformation matrix from the object definition, scale
    # theta, and s and d. The view of the object is created based on the
    # transformation matrix and drawn on the Graphics object g.
    #
    def paint(self, width, height):
        # start with unit diagonal
        self.unit_diagonal(self.view_tm)

        # rotate object
        self.rotx(self.xinc, self.rotx_tm)
        self.am4x4(self.view_tm, self.rotx_tm, self.view_tm)

        self.roty(self.yinc, self.roty_tm)
        self.am4x4(self.view_tm, self.roty_tm, self.view_tm)

        self.rotz(self.zinc, self.rotz_tm)
        self.am4x4(self.view_tm, self.rotz_tm, self.view_tm)

        # scale
        self.scaleit(self.scale, self.scale, self.scale, self.scale_tm)
        self.am4x4(self.view_tm, self.scale_tm, self.view_tm)

        # move coordinates to origin
        self.trans(-self.xe, -self.ye, -self.ze, self.trans_tm)
        self.am4x4(self.view_tm, self.trans_tm, self.view_tm)

        # rotate -90 deg. about x axis
        self.rotx(1.5708, self.rotx_tm)
        self.am4x4(self.view_tm, self.rotx_tm, self.view_tm)

        # rotate -theta about y axis
        theta = math.atan2(-(self.xe - self.xt), -(self.ye - self.yt))
        self.roty(-theta, self.roty_tm)
        self.am4x4(self.view_tm, self.roty_tm, self.view_tm)

        # rotate -phi around x axis
        phi = math.atan2((self.ze - self.zt),
                         math.sqrt(
            (self.xe - self.xt) * (self.xe - self.xt) +
            (self.ye - self.yt) * (self.ye - self.yt)
        )
        )
        self.rotx(-phi, self.rotx_tm)
        self.am4x4(self.view_tm, self.rotx_tm, self.view_tm)

        # change rh to lh coordinates
        self.scaleit(1, 1, -1, self.scale_tm)
        self.am4x4(self.view_tm, self.scale_tm, self.view_tm)

        # add perspective
        if self.persp:
            self.perspect(self.s, self.d, self.persp_tm)
            self.am4x4(self.view_tm, self.persp_tm, self.view_tm)

        # transform the view
        self.am20x4(self.view_tm, self.view)

        # draw the view in width/height

        orgx = width / 2
        orgy = height / 2
        if self.persp:
            for i in range(self.vertnum):
                self.view[i][0] = (orgx * self.view[i][0] /
                                   self.view[i][2]) + orgx
                self.view[i][1] = (orgy * self.view[i][1] /
                                   self.view[i][2]) + orgy
        self.canvas.delete("all")
        for i in range(self.facenum):
            for j in range(self.edgenum[i] - 1):
                self.canvas.create_line(
                    self.view[self.face[i][j]][0],
                    self.view[self.face[i][j]][1],
                    self.view[self.face[i][j + 1]][0],
                    self.view[self.face[i][j + 1]][1],
                    fill='green'
                )
            self.canvas.create_line(
                self.view[self.face[i][j + 1]][0],
                self.view[self.face[i][j + 1]][1],
                self.view[self.face[i][0]][0],
                self.view[self.face[i][0]][1],
                fill='green'
            )
        self.frames += 1
        self.canvas.create_text(20, height-10, fill="green", font="Ariel 10", anchor='sw',
                                text='Object: ' + self.name + '   Frames: ' + str(self.frames) + '   Angle: ' + str(self.yinc))
        self.canvas.update()


#
# main program
#
wireframe = Objectv("House2.txt")
while True:
    wireframe.paint(512, 512)
    wireframe.rotate()
