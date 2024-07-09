from tkinter import *
from tkinter.colorchooser import askcolor
from signature import Signature, SignatureConfigurator

class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = Tk()

        i = 0
        self.pen_button = Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=i)

        i+=1
        self.coord_button = Button(self.root, text='dot-pen', command=self.use_coord)
        self.coord_button.grid(row=0, column=i)

        # i+=1
        # self.brush_button = Button(self.root, text='brush', command=self.use_brush)
        # self.brush_button.grid(row=0, column=i)

        # i+=1
        # self.eraser_button = Button(self.root, text='eraser', command=self.use_eraser)
        # self.eraser_button.grid(row=0, column=i)

        i+=1
        self.undo_button = Button(self.root, text='undo', command=self.use_undo)
        self.undo_button.grid(row=0, column=i)

        i+=1
        self.ce_button = Button(self.root, text="CE", command=self.use_ce)
        self.ce_button.grid(row=0, column=i)

        i+=1
        self.color_button = Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=i)

        i+=1
        self.choose_size_button = Scale(self.root, showvalue=0, label="Size", from_=1, to=10, orient=HORIZONTAL)
        self.choose_size_button.grid(row=0, column=i)

        i+=1
        self.finish_button = Button(self.root, text="finish", command=self.finish)
        self.finish_button.grid(row=0, column=i)

        i = 0
        self.yfade = BooleanVar(value=False)
        self.yfade_button = Checkbutton(self.root, text="Y-Fade", variable=self.yfade, onvalue=True, offvalue=False)
        self.yfade_button.grid(row=1, column=i)

        i+=1
        self.ydrift = BooleanVar(value=False)
        self.ydrift_button = Checkbutton(self.root, text="Y-Drift", variable=self.ydrift, onvalue=True, offvalue=False)
        self.ydrift_button.grid(row=1, column=i)

        i+=1
        self.xstretch = BooleanVar(value=False)
        self.xstretch_button = Checkbutton(self.root, text="X-Stretch", variable=self.xstretch, onvalue=True, offvalue=False)
        self.xstretch_button.grid(row=1, column=i)

        i+=1
        self.jiggle = BooleanVar(value=False)
        self.jiggle_button = Checkbutton(self.root, text="Jiggle", variable=self.jiggle, onvalue=True, offvalue=False)
        self.jiggle_button.grid(row=1, column=i)

        i+=1
        self.velocity = BooleanVar(value=False)
        self.velocity_button = Checkbutton(self.root, text="Velocity", variable=self.velocity, onvalue=True, offvalue=False)
        self.velocity_button.grid(row=1, column=i)

        i+=1
        self.dotshift = BooleanVar(value=False)
        self.dotshift_button = Checkbutton(self.root, text="Dot-Shift", variable=self.dotshift, onvalue=True, offvalue=False)
        self.dotshift_button.grid(row=1, column=i)

        i = 0
        self.stampbox = BooleanVar(value=False)
        self.stampbox_button = Checkbutton(self.root, text="Stamp-Box", variable=self.stampbox, onvalue=True, offvalue=False)
        self.stampbox_button.grid(row=2, column=i)

        # i+=1
        # self.circle = 0
        # self.circle_button = Checkbutton(self.root, text="Stamp-Circle", variable=self.circle, onvalue=True, offvalue=False)
        # self.circle_button.grid(row=2, column=i)

        i+=1
        self.rotational = BooleanVar(value=False)
        self.rotational_button = Checkbutton(self.root, text="Rotational", variable=self.rotational, onvalue=True, offvalue=False)
        self.rotational_button.grid(row=2, column=i)

        i+=1
        self.choose_ink_button = Scale(self.root, showvalue=0, label="Ink", from_=1, to=10, orient=HORIZONTAL)
        self.choose_ink_button.grid(row=2, column=i)

        i+=1
        self.label = Label(self.root, text="Seed:")
        self.label.grid(row=2, column=i)
        i+=1
        self.seed_entry= Entry(self.root, width= 15)
        self.seed_entry.grid(row=2, column=i)

        i+=1
        self.c = Canvas(self.root, bg='white', width=900, height=900)
        self.c.grid(row=3, columnspan=8)

        self.coords = []
        self.splines = []

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.fade = self.choose_ink_button.get()
        self.seed = self.seed_entry.get()
        try:
            self.seed = int(self.seed)
        except:
            self.seed = 0
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button

    def use_undo(self):
        # remove empty array
        print(self.coords)
        if len(self.coords[-1]) == 0:
            del self.coords[-1]

        if len(self.coords) == 0:
            self.reset()
            return

        self.c.delete("all")
        self.old_x, self.old_y = None, None
        for coord in self.coords[-1][:-1]:
            self.paint(None, coord, redraw=True)

        self.coords[-1] = self.coords[-1][:-1]
            

    def use_pen(self):
        self.reset()
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.c.unbind('<ButtonPress-1>')
        self.activate_button(self.pen_button)

    def use_coord(self):
        self.reset()
        self.c.unbind('<B1-Motion>')
        self.c.unbind('<ButtonRelease-1>')
        self.c.bind('<ButtonPress-1>', self.paint)
        self.activate_button(self.coord_button)

    # def use_brush(self):
    #     self.c.bind('<B1-Motion>', self.paint)
    #     self.c.bind('<ButtonRelease-1>', self.reset)
    #     self.c.unbind('<ButtonPress-1>')
    #     self.activate_button(self.brush_button)

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    # def use_eraser(self):
    #     self.c.bind('<B1-Motion>', self.paint)
    #     self.c.bind('<ButtonRelease-1>', self.reset)
    #     self.c.unbind('<ButtonPress-1>')
    #     self.activate_button(self.eraser_button, eraser_mode=True)

    def use_ce(self):
        self.c.delete("all")
        self.coords = []

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event, coord=None, redraw=False):
        x = coord[0] if coord else event.x
        y = coord[1] if coord else event.y
        
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, x, y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = x
        self.old_y = y
        if len(self.coords) == 0:
            self.coords.append([])

        if self.eraser_on == False and redraw == False:
            self.coords[-1].append((x, y))
        
    def finish(self):
        # sig = Signature(self.coords, self.color, self.line_width, 1)
        # sig.write_img("test_sig")
        # sig.write_ps("test_sig")

        sig_config = SignatureConfigurator()
        sig_config.generate_sigs(
            self.coords,
            self.color,
            self.line_width,
            self.fade,

            seed = self.seed,

            yfade = self.yfade.get(),
            ydrift = self.ydrift.get(),
            xstretch = self.xstretch.get(),
            jiggle = self.jiggle.get(),
            velocity = self.velocity.get(),
            dotshift = self.dotshift.get(),
            stampbox = self.stampbox.get(),
            rotational = self.rotational.get(),
        )

    def reset(self, event=None):
        self.old_x, self.old_y = None, None
        self.coords.append([])


if __name__ == '__main__':
    Paint()