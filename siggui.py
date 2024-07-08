from tkinter import *
from PIL import Image, ImageDraw
import numpy as np
import scipy.interpolate as si

import sys
from tkinter import Tk, Button, Frame
from tkinter.scrolledtext import ScrolledText

from signature import write_ps, bspline

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