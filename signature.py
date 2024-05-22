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

tk = Tk()
cvs = Canvas(tk, width=612,height=792)
cvs.pack()

img = Image.new('RGB',(612,792),(255,255,255))
draw = ImageDraw.Draw(img)

splines = []
gcoords = [[]]

mousePressed = False
last=None

#Initialize a Label to display the User Input
label=Label(tk, text="", font=("Courier 22 bold"))
label.pack(side= TOP)

#Create an Entry widget to accept User Input
entry= Entry(tk, width= 40)
entry.pack(side= TOP)

def display_text():
   global entry
   string= entry.get()
   label.configure(text=string)

def press(evt):
    global mousePressed
    mousePressed = True

def release(evt):
    global mousePressed, gcoords
    mousePressed = False
    gcoords.append([])

cvs.bind_all('<ButtonPress-1>', press)
cvs.bind_all('<ButtonRelease-1>', release)

def finish():
    global splines, gcoords

    scale = float(entry.get()) if entry.get() else 1

    for coords in gcoords:
        if len(coords) == 0:
            continue
        spline = bspline(coords, n=int(200*scale))
        spline = spline * scale
        draw.line([(x-50,y-50) for x,y in spline], fill='red', width=2)
        splines.append(spline)

    write_ps("signature.ps", splines)
    img.save('img.png')
    # tk.destroy()
Button(tk,text='done',command=finish).pack()

def move(evt):
    global mousePressed, last, splines, gcoords
    x,y = evt.x,evt.y
    if mousePressed:
        if last is None:
            last = (x,y)
            return
        
        gcoords[-1].append((x,y))
        draw.line(((x,y),last), (0,0,0))
        cvs.create_line(x,y,last[0],last[1])

        last = (x,y)
    else:
        last = (x,y)

cvs.bind_all('<Motion>', move)

tk.mainloop()