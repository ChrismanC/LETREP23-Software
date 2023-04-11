from random import random
from tkinter import *
from PIL import Image, ImageTk
import math
from time import time

#this displays a little bar after the high/good/low preload scale depending on the delay of the M1 wave
class M1Display(Canvas):

    def __init__(self, root, width, height, max, min, threshold, baseline, bar_width=0.5, up=False, *args, **kw):
        super(M1Display, self).__init__(root, width=width, height=height, *args, **kw)
        self.width = width
        self.height = height
        self.pos = 0
        self.min = min
        self.max = max
        self.bar_width = bar_width
        self.threshold = threshold
        self.baseline = baseline
        self.up = up

        #make a lil window
        self._bg = self.create_rectangle(0, 0, width, height, fill="#a8a8a8")
        self._threshold = self.create_rectangle(0, 0, 0, 0, fill="#858585")
        self.update_threshold(threshold, up)

        self._baseline = self.create_rectangle(0, 0, 0, 0, fill="black")
        self.update_baseline(baseline)

        self._bar = self.create_rectangle(0, 0, 0, 0, outline="#000000")
        self.update_position((max + min) / 2)

    #gets y
    def get_y(self, pos):
        return self.height * (1 - (pos - self.min) / (self.max - self.min))

    #updates m1 threshold to threshold
    def update_threshold(self, threshold, up=None):
        self.threshold = threshold
        if up is None:
            up = self.up
        if up:
            self.coords(self._threshold, 0, 0, self.width, self.get_y(threshold))
        else:
            self.coords(self._threshold, 0, self.get_y(threshold), self.width, self.height)

    #updates baseline
    def update_baseline(self, baseline):
        self.baseline = baseline
        y = self.get_y(baseline)
        self.coords(self._baseline, 0, y, self.width, y)

    #updates bounds for max/min m1
    def update_bounds(self, m1min, m1max):
        self.min = m1min
        self.max = m1max

    #update position of bar
    def update_position(self, pos):
        self.pos = pos
        w = self.bar_width * self.width
        x = (1 - self.bar_width) / 2 * self.width
        y = self.get_y(pos)
        h = self.height - y

        self.coords(self._bar, x, y, x + w, y + h)
        color = "#0ed145" if (pos > self.threshold) == self.up else "#ec1c24"
        self.itemconfigure(self._bar, fill=color)

    #update everything
    def update_all(self, threshold=None, baseline=None, m1min=None, m1max=None, pos=None):
        self.update_bounds(m1min if m1min is not None else self.min, m1max if m1max else self.max)
        self.update_threshold(threshold if threshold is not None else self.threshold)
        self.update_baseline(baseline if baseline is not None else self.baseline)
        self.update_position(pos if pos is not None else self.pos)



#lil test run
if __name__ == "__main__":
    root = Tk()
    m1max = 5
    display = M1Display(root, 200, 300, m1max, 0, 3.5, 2.5)
    display.pack()

    prevtime = 0
    while 1:
        if time() - prevtime > 3:
            pos = 5 * random()
            display.update_position(pos)
            prevtime = time()
            m1max += 0.25
            display.update_all(m1max=m1max)
        root.update()
