from tkinter import *
root1 = Tk()
root2 = Tk()
root1.after(5, root1.mainloop) # первый цикл запускаем в фоне
root2.mainloop()