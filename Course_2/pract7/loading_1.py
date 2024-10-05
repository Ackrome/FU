from tkinter import *
from random import *
from math import cos, sin, radians

size=600
root = Tk()
canvas = Canvas(root, width=size, height=size)
canvas.pack()    

canvas.create_oval(100,100,500,500)
ball = canvas.create_oval(290, 90, 310, 110, fill='green')

def move(angle):
    if angle >=360:
        angle = 0
    x = 200  * cos(radians(angle))
    y = 200  * sin(radians(angle))
    angle+=0.1
    canvas.coords(ball,290+x, 290+y, 310+x, 310+y)
    root.after(1, move, angle)
    

root.after(1, move, 0)

root.mainloop()