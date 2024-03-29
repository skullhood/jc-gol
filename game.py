import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from enum import Enum
import random
import time 

#CONSTANTS
WINDOW_TITLE = "Game of Life"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
SCALE = 12

D_WIDTH = int(WINDOW_WIDTH / SCALE)
D_HEIGHT = int(WINDOW_HEIGHT / SCALE)

FRAME_RATE = 5     # how many frames to display per second
TIMESTEP = 1.0 / FRAME_RATE    # how often to refresh the frame

FILL_SEED_CHANCE = 0.15

window = tk.Tk()
#WINDOW STUFF
window.title(WINDOW_TITLE)
window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
window.configure(background='grey')
window.resizable(False, False)

#CELL_UPDATE_ENUM
class CellUpdate(Enum):
    KILL = 1
    NEW = 2

#DISPLAY CLASS
class Display:

    def __init__(self, load):

        self.RUNNING = True
        self.GS_PAUSE = True

        self.point_list = []
        self.update_list = []
        self.checked_list = []

        self.panel = tk.Label(window)
        
        if load == None:
            self.noisefill()
            self.render()

        self.panel.bind("<Button-1>", self.click_l)
        self.panel.bind("<Button-3>", self.click_r)
        self.panel.bind("<space>", self.pause)

        self.panel.pack(side = "bottom", fill = "both", expand = "yes")

    def noisefill(self):
        self.point_list.clear()
        self.data = np.zeros((D_HEIGHT, D_WIDTH), dtype=np.uint8)
        for y in range(D_HEIGHT):
            for x in range(D_WIDTH):
                if random.random() < FILL_SEED_CHANCE:
                    self.data[y][x] = 255
                    self.point_list.append((y,x))

    def click_l(self, event):
        self.panel.focus()

        truex = int(event.x/SCALE)
        truey = int(event.y/SCALE)
        self.data[truey][truex] = 255

        if (truey,truex) not in self.point_list:
            self.point_list.append((truey, truex))

        self.render()

        print("clicked left at", event.x, event.y)

    def click_r(self, event):
        self.panel.focus()

        truex = int(event.x/SCALE)
        truey = int(event.y/SCALE)
        self.data[truey][truex] = 0

        if (truey,truex) in self.point_list:
            self.point_list.remove((truey, truex))

        self.render()

        print("clicked right at", event.x, event.y)

    def pause(self, event):
        if self.GS_PAUSE == True:
            print("=======Unpaused=======")
        else:
            print("=======Paused=======")
        self.GS_PAUSE = not self.GS_PAUSE
        

    def get_num_nei(self, point):
        miny = point[0] - 1 if point[0] - 1 >= 0 else 0
        maxy = point[0] + 1 if point[0] + 1 <= D_HEIGHT - 1 else D_HEIGHT - 1
        minx = point[1] - 1 if point[1] - 1 >= 0 else 0
        maxx = point[1] + 1 if point[1] + 1 <= D_WIDTH - 1 else D_WIDTH - 1

        nn = 0

        y = miny
        while y <= maxy:
            x = minx
            while x <= maxx:
                if y == point[0] and x == point[1]:
                    pass
                else:
                    if self.data[y][x] == 255:
                        nn = nn + 1
                x = x + 1
            y = y + 1

        return nn

    def check_point(self, point):
        if point not in self.checked_list:
    
            nn = self.get_num_nei(point)
            pv = self.data[point[0]][point[1]]        

            if pv == 255:
                if nn < 2:
                    self.update_list.append((point, CellUpdate.KILL))
                elif nn > 3:
                    self.update_list.append((point, CellUpdate.KILL))
            elif pv == 0:
                if nn == 3:
                    self.update_list.append((point, CellUpdate.NEW))
            self.checked_list.append(point)

    def check_nei(self, point):
        miny = point[0] - 1 if point[0] - 1 >= 0 else 0
        maxy = point[0] + 1 if point[0] + 1 <= D_HEIGHT - 1 else D_HEIGHT - 1
        minx = point[1] - 1 if point[1] - 1 >= 0 else 0
        maxx = point[1] + 1 if point[1] + 1 <= D_WIDTH - 1 else D_WIDTH - 1

        y = miny
        while y <= maxy:
            x = minx
            while x <= maxx:
                if y == point[0] and x == point[1]:
                    pass
                else:
                    self.check_point((y,x))
                x = x + 1
            y = y + 1
        
    def update_points(self):
        for op in self.update_list:
            point = op[0]
            operation = op[1]

            if operation == CellUpdate.KILL:
                self.data[point[0]][point[1]] = 0
                if point in self.point_list:
                    self.point_list.remove(point)
            elif operation == CellUpdate.NEW:
                self.data[point[0]][point[1]] = 255
                if point not in self.point_list:
                    self.point_list.append(point)


    def affect(self):
        for point in self.point_list:
            self.check_point(point)
            self.check_nei(point)
        self.update_points()
        self.checked_list.clear()
        self.update_list.clear()

    def render(self):

        data_r = self.data.repeat(SCALE, axis=0).repeat(SCALE, axis=1)

        self.image = Image.fromarray(data_r, "L")
        self.img = ImageTk.PhotoImage(self.image)
        self.panel.configure(image = self.img)

    def tick(self):
        self.affect()
        self.render()

display = Display(None)

#TIMESTEP STUFF
current_time = time.time()
accumulator = 0.0

while display.RUNNING:
    new_time = time.time()
    frame_time = new_time - current_time
    current_time = new_time
    accumulator = accumulator + frame_time
    while accumulator >= TIMESTEP:
        if not display.GS_PAUSE:
            display.tick()
        accumulator = accumulator - TIMESTEP
    alpha = accumulator/ TIMESTEP

    window.update_idletasks()
    window.update()