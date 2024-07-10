from tkinter import *
from PIL import Image, ImageDraw
import numpy as np
import scipy.interpolate as si
import scipy.integrate as it
import scipy.ndimage as ni

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
    degree = np.clip(degree,1,count-1)
    kv = np.array([0]*degree + list(range(count-degree+1)) + [count-degree]*degree,dtype='int')
    u = np.linspace(0,(count-degree),n)
    return np.array(si.splev(u, (kv,cv.T,degree))).T

class SignatureComponent():
    def update_sig(self, seed):
        pass

    def get_sig(self):
        pass

    def write_img(self, fname):
        pass

    def write_ps(self, fname):
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
            spline = bspline(line, n=int(max(len(line)//3,5)))
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
        img = Image.new('RGB',(612,792),(255,255,255))
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
                line += f"{v1[0]} {792 - v1[1]} moveto\n"
                line += f"{v2[0]} {792 - v2[1]} lineto\n"
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
    lengths = None
    splines = None
    color = None
    fade = None
    width = None

    def __init__(self, signature: SignatureComponent, seed=0):
        self._sig = signature
        try: 
            self.seed = int(seed)
        except:
            self.seed = np.random.randint(45871)
        
        self.lengths = signature.lengths
        self.splines = signature.splines
        self.color = signature.color
        self.fade = signature.fade
        self.width = signature.width
        self.update_sig()

        self._sig.lengths = self.lengths
        self._sig.splines = self.splines
        self._sig.color = self.color
        self._sig.fade = self.fade
        self._sig.width = self.width


    @property
    def signature(self) -> SignatureComponent:
        return self._sig

    def update_sig(self):
        return self._sig.update_sig(self.seed)
    
    def get_sig(self):
        return self._sig.get_sig()

    def write_img(self, fname):
        return self._sig.write_img(fname)

    def write_ps(self, fname):
        return self._sig.write_ps(fname)

class SigJiggle(SignatureDecorator):
    def __init__(self, signature: SignatureComponent, xjiggle, yjiggle, seed=0):
        self.xjiggle = xjiggle
        self.yjiggle = yjiggle
        super().__init__(signature, seed)

    def update_sig(self):
        rng = np.random.default_rng(self.seed + 1234)
        acc = rng.normal(0, 0.05, (len(self.splines),2))
        vel = np.stack([
            int(self.xjiggle) * it.cumulative_trapezoid(acc[:,0], initial=0), 
            int(self.yjiggle) * it.cumulative_trapezoid(acc[:,1], initial=0)
        ], axis=-1)
        loc = np.stack([
            it.cumulative_trapezoid(vel[:,0], initial=0), 
            it.cumulative_trapezoid(vel[:,1], initial=0)
        ], axis=-1)
        self.splines += loc

class SigVelocity(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 1324)
        acc = rng.normal(0, 0.04, (len(self.splines),2))
        vel = np.stack([
            it.cumulative_trapezoid(acc[:,0], initial=0), 
            it.cumulative_trapezoid(acc[:,1], initial=0)
        ], axis=-1)
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        cv = np.stack([
            np.concatenate([[0]]+[np.diff(spline, axis=0)[:,0] for spline in splines]),
            np.concatenate([[0]]+[np.diff(spline, axis=0)[:,1] for spline in splines])
        ], axis=-1)
        vel += cv*0.1
        loc = np.stack([
            it.cumulative_trapezoid(vel[:,0], initial=0), 
            it.cumulative_trapezoid(vel[:,1], initial=0)
        ], axis=-1)
        self.splines += loc

class SigDotShift(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 1324)
        acc = rng.normal(0, 1, (len(self.splines),2))
        vel = np.stack([
            np.concatenate([it.cumulative_trapezoid(acc[a:b,0], initial=0) for a,b in zip(self.lengths[:-1], self.lengths[1:])]), 
            np.concatenate([it.cumulative_trapezoid(acc[a:b,1], initial=0) for a,b in zip(self.lengths[:-1], self.lengths[1:])])
        ], axis=-1)
        loc = np.stack([
            np.concatenate([it.cumulative_trapezoid(vel[a:b,0], initial=0) for a,b in zip(self.lengths[:-1], self.lengths[1:])]), 
            np.concatenate([it.cumulative_trapezoid(vel[a:b,1], initial=0) for a,b in zip(self.lengths[:-1], self.lengths[1:])])
        ], axis=-1)
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        noise = [loc[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        zeros = [np.zeros(spline.shape) for spline in splines]
        dot = [len(spline) < 10 for spline in splines]
        dotnoise = [noise[i] if d else zeros[i] for i,d in enumerate(dot)]
        print(dotnoise)
        loc = np.concatenate(dotnoise)
        self.splines += loc

class SigYDrift(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3241)
        diffy = max(self.splines[:,1]) - min(self.splines[:,1])
        minx, maxx = min(self.splines[:,0]), max(self.splines[:,0])
        r = rng.integers(min(-int(diffy/4), -3), max(int(diffy/4), 3))
        r = (r / abs(r)) * max(25, abs(r))
        m = r / (maxx-minx)
        loc = np.stack([
            np.zeros(len(self.splines)),
            [(m*(x-minx)) for x,y in self.splines]
        ], axis=-1)
        self.splines += loc

class SigXDrift(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3124)
        diffx = max(self.splines[:,0]) - min(self.splines[:,0])
        miny, maxy = min(self.splines[:,1]), max(self.splines[:,1])
        r = rng.integers(min(-int(diffx/8), -3), max(int(diffx/10), 3))
        r = (r / abs(r)) * max(15, abs(r))
        m = r / (maxy-miny)
        loc = np.stack([
            [(m*(y-miny)) for x,y in self.splines],
            np.zeros(len(self.splines)),
        ], axis=-1)
        self.splines += loc
        
class SigXStretch(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 4123)
        r = rng.uniform(0.80, 1.2)
        minx, maxx = min(self.splines[:,0]), max(self.splines[:,0])

        diffx = maxx - minx
        nminx, nmaxx = r*minx, r*maxx
        ndiffx = nmaxx - nminx

        self.splines = np.stack([
            [((x-minx)/diffx)*ndiffx + nminx for x in self.splines[:,0]],
            self.splines[:,1]
        ], axis=-1)
        minx, maxx = min(self.splines[:,0]), max(self.splines[:,0])


class SigYStretch(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 4123)
        r = rng.uniform(0.70, 1.3)
        miny, maxy = min(self.splines[:,1]), max(self.splines[:,1])

        diffy = maxy - miny
        nminy, nmaxy = r*miny, r*maxy
        ndiffy = nmaxy - nminy

        self.splines = np.stack([
            self.splines[:,0],
            [((y-miny)/diffy)*ndiffy + nminy for y in self.splines[:,1]]
        ], axis=-1)
        miny, maxy = min(self.splines[:,1]), max(self.splines[:,1])


class SigRotate(SignatureDecorator):
    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3411)
        th = rng.uniform(-15, 15)
        cx, cy = np.mean(self.splines[:,0]), np.mean(self.splines[:,1])

        self.splines = np.stack([
           self.splines[:,0]-cx,
           self.splines[:,1]-cy
        ], axis=-1)

        self.splines = np.stack([
           [(x*np.cos(th) - y*np.sin(th))+cx for x, y in self.splines],
           [(x*np.sin(th) + y*np.cos(th))+cy for x, y in self.splines]
        ], axis=-1)

class SignatureConfigurator():
    def generate_sigs(self, coords, color, width, fade, **kwargs):
        seed = kwargs.get('seed', 0)

        sig = Signature(coords, color, width, fade)
        
        sig.write_img('prev_sig')
        sig.write_ps('prev_sig')

        xjiggle, yjiggle = kwargs['jiggle']
        if xjiggle | yjiggle:
            print("jiggle")
            print(sig.splines[:5])
            sig = SigJiggle(sig, xjiggle, yjiggle, seed)
            print(sig.splines[:5])

        if kwargs['velocity']:
            print("velocity")
            print(sig.splines[:5])
            sig = SigVelocity(sig, seed)
            print(sig.splines[:5])

        if kwargs['dotshift']:
            print("dotshift")
            print(sig.splines[:5])
            sig = SigDotShift(sig, seed)
            print(sig.splines[:5])

        if kwargs['ydrift']:
            print("ydrift")
            print(sig.splines[:5])
            sig = SigYDrift(sig, seed)
            print(sig.splines[:5])

        if kwargs['xdrift']:
            print("xdrift")
            print(sig.splines[:5])
            sig = SigXDrift(sig, seed)
            print(sig.splines[:5])

        if kwargs['xstretch']:
            print("xstretch")
            print(sig.splines[:5])
            sig = SigXStretch(sig, seed)
            print(sig.splines[:5])

        if kwargs['ystretch']:
            print("ystretch")
            print(sig.splines[:5])
            sig = SigYStretch(sig, seed)
            print(sig.splines[:5])

        if kwargs['rotate']:
            print("rotate")
            print(sig.splines[:5])
            sig = SigRotate(sig, seed)
            print(sig.splines[:5])

        sig.write_img('test_sig')
        sig.write_ps('test_sig')




    



