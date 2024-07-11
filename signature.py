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
            spline = bspline(line, n=int(max(len(line)//2, 9)))
            self.splines.append(spline)

        a = 0
        self.lengths = [0]+[a:=a+len(spline) for spline in self.splines]
        self.splines = np.concatenate(self.splines)
        self.color = np.zeros((len(self.splines), 3)) + color
        self.fade = np.ones(len(self.splines)) * (fade/10)
        self.width = np.ones(len(self.splines)) * width

        print(width, color, ((fade)/10))
        print(self.lengths)

    def update_sig(self, seed):
        pass

    def get_sig(self):
        print(self.splines[:10])
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        colors = [self.color[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        fades = [self.fade[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        widths = [self.width[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        return splines, colors, fades, widths
    
    def write_img(self, fname):
        img = Image.new('RGB',(612,792),(255,255,255))
        draw = ImageDraw.Draw(img)
        splines, colors, fades, widths = self.get_sig()
        for spline, color, fade, width in zip(splines, colors, fades, widths):
            if len(spline) == 0:
                continue
            for v1, v2, c, f, w in zip(spline[:-1], spline[1:], color[1:], fade[1:], width[1:]):
                draw.line([(v1[0], v1[1]),(v2[0],v2[1])], fill=(int(c[0]), int(c[1]), int(c[2])), width=int(w))
        img.save(f'./{fname}.png')

    def write_ps(self, fname):
        line = ""
        splines, colors, fades, widths = self.get_sig()
        print(len(splines))
        for spline, color, fade, width in zip(splines, colors, fades, widths):
            for v1, v2, c, f, w in zip(spline[:-1], spline[1:], color[1:], fade[1:], width[1:]):
                line += "newpath\n"
                line += f"{c[0]/256} {c[1]/256} {c[2]/256} setrgbcolor\n"
                if int(c[0]) + int(c[0]) + int(c[0]) == 0:
                    line += f"{min(f,0.8)} setgray\n"
                line += f"{v1[0]} {792 - v1[1]} moveto\n"
                line += f"{v2[0]} {792 - v2[1]} lineto\n"
                line += f"1 setlinecap\n"
                line += f"{w} setlinewidth\n"
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

    @property
    def signature(self) -> SignatureComponent:
        return self._sig

    def update_sig(self):
        return self._sig.update_sig(self.seed)
    
    def get_sig(self):
        print(self.splines[:10])
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        colors = [self.color[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        fades = [self.fade[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        widths = [self.width[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        return splines, colors, fades, widths
    
    def write_img(self, fname):
        img = Image.new('RGB',(612,792),(255,255,255))
        draw = ImageDraw.Draw(img)
        splines, colors, fades, widths = self.get_sig()
        for spline, color, fade, width in zip(splines, colors, fades, widths):
            if len(spline) == 0:
                continue
            for v1, v2, c, f, w in zip(spline[:-1], spline[1:], color[1:], fade[1:], width[1:]):
                draw.line([(v1[0], v1[1]),(v2[0],v2[1])], fill=(int(c[0]), int(c[1]), int(c[2])), width=int(w))
        img.save(f'./{fname}.png')

    def write_ps(self, fname):
        line = ""
        splines, colors, fades, widths = self.get_sig()
        print(len(splines))
        for spline, color, fade, width in zip(splines, colors, fades, widths):
            for v1, v2, c, f, w in zip(spline[:-1], spline[1:], color[1:], fade[1:], width[1:]):

                line += "newpath\n"
                line += f"{c[0]/256} {c[1]/256} {c[2]/256} setrgbcolor\n"
                if int(c[0]) + int(c[0]) + int(c[0]) == 0:
                    line += f"{min(f,0.8)} setgray\n"
                line += f"{v1[0]} {792 - v1[1]} moveto\n"
                line += f"{v2[0]} {792 - v2[1]} lineto\n"
                line += f"1 setlinecap\n"
                line += f"{w} setlinewidth\n"
                line += f"stroke\n"
        line += "showpage\n"
        with open(f'./{fname}.ps', 'w') as f:
            f.writelines(line)

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
        print(self.lengths)
        dot = [len(spline) < 10 for spline in splines]
        dotnoise = [noise[i] if d else zeros[i] for i,d in enumerate(dot)]
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
    def __init__(self, signature: SignatureComponent, seed=0):
        super().__init__(signature, seed)

    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3411)
        th = rng.uniform(0, 0.3)
        print(th)
        cx, cy = np.mean(self.splines[:,0]), np.mean(self.splines[:,1])

        splines = np.stack([
           self.splines[:,0]-cx,
           self.splines[:,1]-cy
        ], axis=-1)

        self.splines = np.stack([
           [(x*np.cos(th) - y*np.sin(th))+cx for x, y in splines],
           [(x*np.sin(th) + y*np.cos(th))+cy for x, y in splines]
        ], axis=-1)

class SigYFade(SignatureDecorator):
    def __init__(self, signature: SignatureComponent, width, fade, seed=0):
        self.w = width
        self.f = fade
        super().__init__(signature, seed)

    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3411)
        pen = rng.uniform(1.05, 1.4)
        diff = rng.uniform(0.4,0.75)
        af = rng.uniform(0.2,0.5)

        miny, meany, maxy = min(self.splines[:,1]), np.mean(self.splines[:,1]), max(self.splines[:,1])
        stdy = np.std(self.splines[:,1])
        
        le = lambda y, p1, p2: (p1[1] - p2[1])/(p1[0] - p2[0]) * (y - p1[0]) + p1[1]

        lew = lambda y: le(y, (miny + stdy, self.w), (miny, (pen - diff)*self.w))
        self.width = np.array(
            [lew(y) if y < (miny + stdy) else w for y, w in zip(self.splines[:,1], self.width)]
        )
        lef = lambda y: le(y, (miny + stdy, self.f), (miny, af))
        self.fade = np.array(
            [lef(y) if y < (miny + stdy) else w for y, w in zip(self.splines[:,1], self.fade)]
        )
        lew = lambda y: le(y, (meany, pen*self.w), (meany-stdy, self.w))
        self.width = np.array(
            [lew(y) if ((meany - stdy) < y) & (y < meany) else w for y, w in zip(self.splines[:,1], self.width)]
        )
        lew = lambda y: le(y, (meany+stdy, self.w), (meany, pen*self.w))
        self.width = np.array(
            [lew(y) if (meany < y) & ((meany + stdy) < y) else w for y, w in zip(self.splines[:,1], self.width)]
        )
        lef = lambda y: le(y, (maxy, af), (maxy-stdy, self.f))
        self.fade = np.array(
            [lef(y) if (maxy - stdy) < y else w for y, w in zip(self.splines[:,1], self.fade)]
        )
        lew = lambda y: le(y, (maxy, (pen - diff)*self.w), (maxy-stdy, self.w))
        self.width = np.array(
            [lew(y) if (maxy - stdy) < y else w for y, w in zip(self.splines[:,1], self.width)]
        )

class SigVelFade(SignatureDecorator):
    def __init__(self, signature: SignatureComponent, width, fade, seed=0):
        self.w = width
        self.f = fade
        super().__init__(signature, seed)

    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3411)
        pen = rng.uniform(1.05, 1.4)
        diff = rng.uniform(0.4,0.75)
        af = rng.uniform(0.2,0.5)

        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        # v = np.stack([
        #     np.concatenate([[0]]+[np.diff(spline, axis=0)[:,0] for spline in splines]),
        #     np.concatenate([[0]]+[np.diff(spline, axis=0)[:,1] for spline in splines])
        # ], axis=-1)

        v = np.concatenate([[0,0,0,0]+[
            np.dot(
            (spline[i][0]-spline[i-4][0],spline[i][1]-spline[i-4][1]),
            (spline[i][0]-spline[i-1][0],spline[i][1]-spline[i-1][1])) 
            + 
            np.dot(
            (spline[i][0]-spline[i-4][0],spline[i][1]-spline[i-4][1]),
            (spline[i][0]-spline[i-2][0],spline[i][1]-spline[i-2][1]))
            for i in range(4, len(spline))] for spline in splines])

        minv, meanv, maxv = min(v), np.mean(v), max(v)
        stdv = np.std(v)

        le = lambda y, p1, p2: (p1[1] - p2[1])/(p1[0] - p2[0]) * (y - p1[0]) + p1[1]

        lew = lambda y: le(y, (maxv, (pen - diff)*self.w), (meanv, self.w))
        self.width = np.array(
            [lew(y) if (meanv) < y else w for y, w in zip(v, self.width)]
        )
        lef = lambda y: le(y, (maxv, af), (meanv, self.f))
        self.fade = np.array(
            [lef(y) if (meanv) < y else w for y, w in zip(v, self.fade)]
        )
        lew = lambda y: le(y, (meanv, self.w), (minv, (pen-diff)*self.w))
        self.width = np.array(
            [lew(y) if y < (meanv) else w for y, w in zip(v, self.width)]
        )

class SigStampBox(SignatureDecorator):
    def __init__(self, signature: SignatureComponent, color, width, fade, seed=0):
        if color == "black":
            color = "#000000"
        color = color.lstrip('#')
        color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        self.c = color
        self.w = width+2
        self.f = fade // 10
        super().__init__(signature, seed)

    def update_sig(self):
        minx, maxx = min(self.splines[:,0])-10, max(self.splines[:,0])+10
        miny, maxy = min(self.splines[:,1])-10, max(self.splines[:,1])+10
        
        length = [self.lengths[-1] + 5]
        spline = [
            [minx, miny],
            [minx, maxy],
            [maxx, maxy],
            [maxx, miny],
            [minx, miny]
        ]
        color = np.zeros((5,3)) + self.c
        fade = np.ones(5)*self.f
        width = np.ones(5)*self.w

        self.lengths = np.append(self.lengths, length)
        self.splines = np.append(self.splines, spline, axis=0)
        self.color = np.append(self.color, color, axis=0)
        self.fade = np.append(self.fade, fade)
        self.width = np.append(self.width, width)

class SigStartEndFade(SignatureDecorator):
    def __init__(self, signature: SignatureComponent, width, fade, seed=0):
        self.w = width
        self.f = fade
        super().__init__(signature, seed)

    def update_sig(self):
        rng = np.random.default_rng(self.seed + 3411)
        pen = rng.uniform(1.05, 1.4)
        diff = rng.uniform(0.4,0.75)
        af = rng.uniform(0.2,0.5)
        start = rng.integers(0, int(len(self.splines)//6))
        end = rng.integers(0, int(len(self.splines)//6))

        le = lambda y, p1, p2: (p1[1] - p2[1])/(p1[0] - p2[0]) * (y - p1[0]) + p1[1]

        lew = lambda y: le(y, (start, self.w), (0, (pen - diff)*self.w))
        self.width = np.array(
            [lew(i) if i < start else w for i, w in enumerate(self.width)]
        )

        lew = lambda y: le(y, (start, af), (0, self.f))
        self.fade = np.array(
            [lew(i) if i < start else w for i, w in enumerate(self.fade)]
        )

        lew = lambda y: le(y, (len(self.splines), (pen - diff)*self.w), (len(self.splines)-end, self.w))
        self.width = np.array(
            [lew(i) if (len(self.splines)-end) < i else w for i, w in enumerate(self.width)]
        )

        lew = lambda y: le(y, (len(self.splines), af), (len(self.splines)-end, self.f))
        self.fade = np.array(
            [lew(i) if (len(self.splines)-end) < i else w for i, w in enumerate(self.fade)]
        )

class SigSmooth(SignatureDecorator):
    def update_sig(self):
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        width = [self.width[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        color = [self.color[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]
        fade = [self.fade[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]

        dsplines = [
            [[2]+np.sqrt((x2-x1)**2 + (y2-y1)**2) for (x1,y1), (x2,y2) in zip(spline[:-1], spline[1:])]
            for spline in splines
        ]

        print(dsplines)

        bools = [
            [d > 1.75*w for d,w in zip(dspline, ws)] 
            for dspline, ws in zip(dsplines, width)
        ]

        print(self.lengths)
        self.lengths = [0]+[sum(b)[0] for b in bools]
        print(self.lengths)
        self.splines = np.concatenate([[v for v,b in zip(spline, bs) if b] for spline, bs in zip(splines, bools)])
        self.width = np.concatenate([[v for v,b in zip(ws, bs) if b] for ws, bs in zip(width, bools)])
        self.color = np.concatenate([[v for v,b in zip(cs, bs) if b] for cs, bs in zip(color, bools)])
        self.fade = np.concatenate([[v for v,b in zip(fs, bs) if b] for fs, bs in zip(fade, bools)])

class SigSmoothK(SignatureDecorator):
    def update_sig(self):
        splines = [self.splines[a:b] for a,b in zip(self.lengths[:-1], self.lengths[1:])]

        splines1 = np.concatenate([
            np.append(np.stack([
                np.convolve(spline[:,0], [0.45, 0.1, 0.45], mode='valid'),
                np.convolve(spline[:,1], [0.45, 0.1, 0.45], mode='valid'),
            ], axis=-1), spline[-2:], axis=0) 
            for spline in splines
        ])

        splines2 = np.concatenate([
            np.append(np.stack([
                np.convolve(spline[:,0], [0.45, 0.05, 0.05, 0.45], mode='valid'),
                np.convolve(spline[:,1], [0.45, 0.05, 0.05, 0.45], mode='valid'),
            ], axis=-1), spline[-3:], axis=0)
            for spline in splines
        ])

        splines3 = np.concatenate([
            np.append(np.stack([
                np.convolve(spline[:,0], [0.45, 0, 0.1, 0, 0.45], mode='valid'),
                np.convolve(spline[:,1], [0.45, 0, 0.1, 0, 0.45], mode='valid'),
            ], axis=-1), spline[-4:], axis=0)
            for spline in splines
        ])

        self.splines = (splines1 + splines2 + splines3) / 3
        

class SignatureConfigurator():
    def generate_sigs(self, coords, color, width, fade, **kwargs):
        seed = kwargs.get('seed', 0)

        sig = Signature(coords, color, width, fade)
        
        sig.write_img('prev_sig')
        sig.write_ps('prev_sig')

        kl = len(kwargs) + 1
        dl = np.zeros(kl)
        if kwargs['surprise']:
            dl = np.random.randint(0,2, kl)

        i=0
        if kwargs['yfade'] + dl[i]:
            print("yfade")
            print(sig.splines[:5])
            sig = SigYFade(sig, width, fade, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['velfade'] + dl[i]:
            print("velfade")
            print(sig.splines[:5])
            sig = SigVelFade(sig, width, fade, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['startendfade'] + dl[i]:
            print("startendfade")
            print(sig.splines[:5])
            sig = SigStartEndFade(sig, width, fade, seed)
            print(sig.splines[:5])

        i+=1
        xjiggle, yjiggle = kwargs['jiggle']
        xjiggle += dl[i]
        i+=1
        yjiggle += dl[i]
        if xjiggle + yjiggle:
            print("jiggle")
            print(sig.splines[:5])
            sig = SigJiggle(sig, xjiggle, yjiggle, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['velocity'] + dl[i]:
            print("velocity")
            print(sig.splines[:5])
            sig = SigVelocity(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['dotshift'] + dl[i]:
            print("dotshift")
            print(sig.splines[:5])
            sig = SigDotShift(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['ydrift'] + dl[i]:
            print("ydrift")
            print(sig.splines[:5])
            sig = SigYDrift(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['xdrift'] + dl[i]:
            print("xdrift")
            print(sig.splines[:5])
            sig = SigXDrift(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['xstretch'] + dl[i]:
            print("xstretch")
            print(sig.splines[:5])
            sig = SigXStretch(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['ystretch'] + dl[i]:
            print("ystretch")
            print(sig.splines[:5])
            sig = SigYStretch(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['smoothk'] + dl[i]:
            print("smoothk")
            print(sig.splines[:5])
            sig = SigSmoothK(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['smooth']:
            print("smooth")
            print(sig.splines[:5])
            sig = SigSmooth(sig, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['stampbox']:
            print("stampbox")
            print(sig.splines[:5])
            sig = SigStampBox(sig, color, width, fade, seed)
            print(sig.splines[:5])

        i+=1
        if kwargs['rotate']:
            print("rotate")
            print(sig.splines[:5])
            sig = SigRotate(sig, seed)
            print(sig.splines[:5])
        
        print("end")
        sig.write_img('test_sig')
        sig.write_ps('test_sig')




    



