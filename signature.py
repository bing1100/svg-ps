from tkinter import *
from PIL import Image, ImageDraw
import numpy as np
import scipy.interpolate as si
import scipy.integrate as it

import sys
from tkinter import Tk, Button, Frame
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageDraw

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

class SignatureComponent():
    def update_sig(self, seed):
        pass

class Signature(SignatureComponent):
    def __init__(self, coords, color, width, fade) -> None:
        if color == "black":
            color = "#000000"
        color = color.lstrip('#')
        color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        self.splines = []
        for line in coords:
            if len(line) == 0:
                continue
            spline = bspline(line, n=int(len(line)//3))
            self.splines.append(spline)

        a = 0
        self.lengths = [0]+[a:=a+len(spline) for spline in self.splines]
        self.splines = np.concatenate(self.splines)
        self.color = np.zeros((len(self.splines), 3)) + color
        self.fade = np.ones(len(self.splines)) * ((fade-1)/10)
        self.width = np.ones(len(self.splines)) * width

        print(self.lengths)

    def update_sig(self, seed):
        pass

    def get_sig(self):
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        colors = [self.color[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        fades = [self.fade[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        widths = [self.width[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        return splines, colors, fades, widths
    
    def write_img(self, fname):
        img = Image.new('RGB',(900,900),(255,255,255))
        draw = ImageDraw.Draw(img)
        splines, _, _, _ = self.get_sig()
        for spline in splines:
            if len(spline) == 0:
                continue
            draw.line([(x,y) for x,y in spline], fill='red', width=2)
        img.save(f'./{fname}.png')

    def write_ps(self, fname):
        line = ""
        splines, colors, fades, widths = self.get_sig()
        for spline, color, fade, width in zip(splines, colors, fades, widths):
            for v1, v2, c, f, w in zip(spline[:-1], spline[1:], color[1:], fade[1:], width[1:]):
                line += "newpath\n"
                line += f"{v1[0]} {900 - v1[1]} moveto\n"
                line += f"{v2[0]} {900 - v2[1]} lineto\n"
                line += f"1 setlinecap\n"
                line += f"{w} setlinewidth\n"
                line += f"{c[0]} {c[1]} {c[2]} setrgbcolor\n"
                line += f"{f} setgray\n"
                line += f"stroke\n"
        line += "showpage\n"
        with open(f'./{fname}.ps', 'w') as f:
            f.writelines(line)

class SignatureDecorator(SignatureComponent):
    _sig: SignatureComponent = None

    def __init__(self, signature, seed=0):
        self._sig = signature
        self.seed = seed
        self.update_sig()
    
    @property
    def signature(self) -> SignatureComponent:
        return self._sig

    def update_sig(self):
        return self._sig.update_sig(self.seed)

class SigJiggle(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 1234)
        a = rng.normal(0, 0.1, (len(self.signature.splines),2))
        v = np.stack([
            it.cumulative_trapezoid(a[:,0], initial=0), 
            it.cumulative_trapezoid(a[:,0], initial=0)
        ], axis=-1)
        l = np.stack([
            it.cumulative_trapezoid(v[:,0], initial=0), 
            it.cumulative_trapezoid(v[:,0], initial=0)
        ], axis=-1)
        print(l)
        print(l.shape)
        print(self.signature.splines.shape)
        self.signature.splines += l

class SignatureConfigurator():
    def generate_sigs(self, coords, color, width, fade, **kwargs):
        sig = Signature(coords, color, width, fade)
        seed = kwargs.get('seed', 0)

        if kwargs['jiggle']:
            sig = SigJiggle(sig, seed)

        sig.signature.write_img('test_sig')
        sig.signature.write_ps('test_sig')




    



