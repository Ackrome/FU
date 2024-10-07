from tkinter import *
import numpy as np

def lorenz(xyz, s=10, r=28, b=2.667):
    """
    Parameters
    ----------
    xyz : array-like, shape (3,)
       Point of interest in three-dimensional space.
    s, r, b : float
       Parameters defining the Lorenz attractor.

    Returns
    -------
    xyz_dot : array, shape (3,)
       Values of the Lorenz attractor's partial derivatives at *xyz*.
    """
    x, y, z = xyz
    x_dot = s*(y - x)
    y_dot = r*x - y - x*z
    z_dot = x*y - b*z
    return np.array([x_dot, y_dot, z_dot])

def dec2hex(rgb):
    """Makes string color code in form of #??? from array

    Args:
        rgb (array): array from numbers under 255

    Returns:
        string: color code in form of #???
    """
    r,g,b=rgb
    return f'#{r:02x}{g:02x}{b:02x}'

def paint(x,y,bs=4):
    """Makes point in global canvas (x,y)

    Args:
        x (int|float): x-coordinate of point
        y (int|float): y-coordinate of point
        bs (int, optional): refers to ball size in pixels. Defaults to 4.
    """
    global canvas
    x1, y1 = (x - bs/2), (y - bs/2)
    x2, y2 = (x + bs/2), (y + bs/2)
    canvas.create_oval(x1, y1, x2, y2,outline='')
    


def move(xyzs,s,r,b,dt,k=0):
    """ Makes one iteration in Lorenz Attractor

    Args:
        xyzs (array): previous point
        s,r,b (_type_): parameters of Lorenz System
        dt (_type_): gradient coefficient or speed of moving
        k (int, optional): colour constant. It defers in each iteration for point to be different colour. Defaults to 0.
    """
    global keep
    xyz_new=xyzs+lorenz(xyzs,s,r,b)*dt
    x,y=xyz_new[0:2]*size**0.34+size_array
    paint(x,y)
    k+=1
    for i in canvas.find_all():
        canvas.itemconfig(i, fill=dec2hex(rgbs[:,k%rgbs.shape[1]]))
    keep = root.after(1, move,xyz_new,s,r,b,dt,k)  

def resetAll():
    """Resets and creates new canvas
    """
    global keep
    global canvas
    canvas.destroy()
    root.after_cancel(keep)
    canvas = Canvas(root, width=size, height=size)
    
    canvas.configure(bg='black')
    canvas.grid(row=4,column=1)
    keep = root.after(1, move,xyz,s.get(),r.get(),b.get(),dt.get(),0)


    
size=500
ball_size=10
size_array=np.array([size/2,size/2])
rgbs=(np.stack((np.arange(0,256),np.arange(0,256),np.arange(255,-1,-1)), axis=0))

root = Tk()

s = Scale(root,label='s', from_=-20, to=20, orient=HORIZONTAL,length = size,digits = 4,resolution =   0.001,var=DoubleVar(value=10) )
s.grid(row=0,column=0)
r = Scale(root,label='r', from_=-50, to=50, orient=HORIZONTAL,length = size,digits = 4,resolution =   0.001,var=DoubleVar(value=28) )
r.grid(row=1,column=0)
b = Scale(root,label='b', from_=-5, to=5, orient=HORIZONTAL,length = size,digits = 4,resolution =   0.001,var=DoubleVar(value=2.667) )
b.grid(row=2,column=0)

x = Scale(root,label='x', from_=-10, to=10, orient=HORIZONTAL,length = size,digits = 4,resolution =   0.001,var=DoubleVar(value=0) )
x.grid(row=0,column=1)
y = Scale(root,label='y', from_=-10, to=10, orient=HORIZONTAL,length = size,digits = 4,resolution =   0.001,var=DoubleVar(value=1) )
y.grid(row=1,column=1)
z = Scale(root,label='z', from_=-10, to=10, orient=HORIZONTAL,length = size,digits = 4,resolution =   0.001,var=DoubleVar(value=1.05) )
z.grid(row=2,column=1)

dt = Scale(root,label='Speed', from_=1e-6, to=0.02, orient=HORIZONTAL,length = size,digits = 5,resolution =   0.00001,var=DoubleVar(value=0.01) )
dt.grid(row=0,column=2)

xyz=[x.get(),y.get(),z.get()]

Button(root, text='Reset to view with new params', command=resetAll).grid(row=1,column=2)

canvas = Canvas(root, width=size, height=size)
canvas.configure(bg='black')
canvas.grid(row=4,column=1)
root.after(1, move,xyz,s.get(),r.get(),b.get(),dt.get(),0)


root.mainloop()
