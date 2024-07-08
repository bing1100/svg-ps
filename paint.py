from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import Image, ImageDraw

class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = Tk()

        i = 0
        self.pen_button = Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=i)

        i+=1
        self.coord_button = Button(self.root, text='coord', command=self.use_coord)
        self.coord_button.grid(row=0, column=i)

        i+=1
        self.brush_button = Button(self.root, text='brush', command=self.use_brush)
        self.brush_button.grid(row=0, column=i)

        i+=1
        self.color_button = Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=i)

        i+=1
        self.eraser_button = Button(self.root, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=i)

        i+=1
        self.undo_button = Button(self.root, text='undo', command=self.use_undo)
        self.undo_button.grid(row=0, column=i)

        i+=1
        self.ce_button = Button(self.root, text="CE", command=self.use_ce)
        self.ce_button.grid(row=0, column=i)
        
        i+=1
        self.choose_size_button = Scale(self.root, from_=1, to=10, orient=HORIZONTAL)
        self.choose_size_button.grid(row=0, column=i)

        i+=1
        self.c = Canvas(self.root, bg='white', width=612, height=792)
        self.c.grid(row=1, columnspan=i)

        self.coords = [[]]
        self.splines = []

        self.img = Image.new('RGB', (612, 792), (255,255,255))
        self.draw = ImageDraw.Draw(self.img)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
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
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.c.unbind('<ButtonPress-1>')
        self.activate_button(self.pen_button)

    def use_coord(self):
        self.c.unbind('<B1-Motion>')
        self.c.unbind('<ButtonRelease-1>')
        self.c.bind('<ButtonPress-1>', self.paint)
        self.activate_button(self.coord_button)

    def use_brush(self):
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.c.unbind('<ButtonPress-1>')
        self.activate_button(self.brush_button)

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    def use_eraser(self):
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.c.unbind('<ButtonPress-1>')
        self.activate_button(self.eraser_button, eraser_mode=True)

    def use_ce(self):
        self.c.delete("all")
        self.coords = [[]]
        self.splines = []

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
        if self.eraser_on == False and redraw == False:
            self.coords[-1].append((x, y))


    def reset(self, event=None):
        self.old_x, self.old_y = None, None
        self.coords.append([])


if __name__ == '__main__':
    Paint()