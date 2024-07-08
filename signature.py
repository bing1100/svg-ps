from tkinter import *
from PIL import Image, ImageDraw
import numpy as np
import scipy.interpolate as si

import sys
from tkinter import Tk, Button, Frame
from tkinter.scrolledtext import ScrolledText

def write_ps(fname, splines):
    line = ""
    for spline in splines:
        line += "newpath\n"
        line += "{} {} moveto\n".format(spline[0][0], 792-spline[0][1])
        for v in spline[1:]:
            line += "{} {} lineto\n".format(v[0], 792-v[1])
        line += "2 setlinewidth\n"
        line += "stroke\n"
    line += "showpage\n"

    with open("./"+fname, 'w') as f:
        f.writelines(line)
    

def bspline(cv, n=100, degree=3):
    """ Calculate n samples on a bspline

        cv :      Array ov control vertices
        n  :      Number of samples to return
        degree:   Curve degree
    """
    cv = np.asarray(cv)
    count = cv.shape[0]

    # Prevent degree from exceeding count-1, otherwise splev will crash
    degree = np.clip(degree,1,count-1)

    # Calculate knot vector
    kv = np.array([0]*degree + list(range(count-degree+1)) + [count-degree]*degree,dtype='int')

    # Calculate query range
    u = np.linspace(0,(count-degree),n)

    # Calculate result
    return np.array(si.splev(u, (kv,cv.T,degree))).T

