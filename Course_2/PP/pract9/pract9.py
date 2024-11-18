import tkinter as tk
from tkinter import ttk
import numpy as np
from heapq import heappop, heappush
import time
import os
import re
##############################################################################################
# Поиск всех файлов с расширением .txt
##############################################################################################
# Шаблон для проверки
pattern = r"^maze_\d+\.txt$"
# Путь к директории
directory = "./"
# Список всех файлов
txts = []
try_number = 0
# Вывод всех файлов с расширением .txt
for file in os.listdir(directory):
    if re.match(pattern, file):
        try_number+=1
    if file.endswith(".txt"):
        txts.append(file)
check_choic = 0
##############################################################################################
# Константы
##############################################################################################
WIDTH=HEIGHT = 70  # Размеры сетки
CELL_SIZE = 10  # Размер клетки в пикселях
WIDTH = WIDTH//2 *2+1
HEIGHT = HEIGHT//2 *2+1
minus_wealls = int(HEIGHT**1.6) #int(HEIGHT*WIDTH**0.6)

# Цвета для визуализации
WALL_COLOR = "black"
EMPTY_COLOR = "white"
START_COLOR = "green"
END_COLOR = "red"
PATH_COLOR = "pink"
FINAL_COLOR = "yellow"
VISITED_COLOR = "blue"
OPEN_COLOR = 'lightgreen'

# Создаем лабиринт с пустыми клетками и стенами]
start = (0, 0)  # Начальная точка
end = (HEIGHT - 1, WIDTH - 1)  # Целевая точка 
# Визуализация с помощью Tkinter
algo_list=['a_star','b_star']
maze = []
##############################################################################################
# Сгенерируем поляну
##############################################################################################
class Cell():
    def __init__(self, x,y,if_not_wall=0,been_here=0):
        self.x=x
        self.y=y
        self.if_not_wall = if_not_wall ### 1 - проход, 0 - стена
        self.been_here=been_here       ### 1 - посещена, 0 - не посещена
        self.rect_obj = None
        
def in_bounds(x, y):
    return 0 <= x < HEIGHT and 0 <= y < WIDTH

def neighbors(x, y,distance=1):
    """ Возвращает соседние клетки (вверх, вниз, влево, вправо) """
    
    for dx, dy in [(-distance, 0), (distance, 0), (0, -distance), (0, distance)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < HEIGHT and 0 <= ny < WIDTH:
            if maze[ny][nx].if_not_wall==1 and maze[ny][nx].been_here==0:
                yield maze[ny][nx]

def removeWall(cell_1,cell_2):
    delta_x=cell_1.x-cell_2.x
    delta_y=cell_1.y-cell_2.y
    add_x = (delta_x / abs(delta_x)) if delta_x!=0 else 0 
    add_y = (delta_y / abs(delta_y)) if delta_y!=0 else 0
    maze[cell_1.x+add_x][cell_1.y+add_y].been_here=1
    maze[cell_1.x+add_x][cell_1.y+add_y].if_not_wall=1
    
def generate_maze(size,WIDTH,HEIGHT):
    maze = [[Cell(j,i,1) for i in range(WIDTH)] for j in range(HEIGHT)]
    m_cords=[str((i,j)) for i in range(HEIGHT) for j in range(WIDTH)]
    
    exclude_list=np.random.choice(m_cords,size,False)

    for i in range(HEIGHT):
        for j in range(WIDTH):
            if str((i,j)) in exclude_list:
                maze[i][j].if_not_wall=0
    return maze

def scan_maze(maze):
    maze = [[Cell(j,i,maze[j,i]) for i in range(maze.shape[1])] for j in range(maze.shape[0])]
    return maze
##############################################################################################
# Перейдем к алгоритмам поиска пути
##############################################################################################
def in_bounds(x, y):
    return 0 <= x < HEIGHT and 0 <= y < WIDTH

def neighbors(x, y, HEIGHT, WIDTH):
    """ Возвращает соседние клетки (вверх, вниз, влево, вправо) """
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
            yield ny, nx
            
def heuristic(a, b):
    """ Эвристика: манхэттенское расстояние """
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def b_star(start, goal, maze):
    """ Реализация алгоритма B* """
    HEIGHT = maze.shape[0]
    WIDTH = maze.shape[1]
    open_list = []
    heappush(open_list, (0, start))  # Начальная стоимость 0 для старта
    came_from = {}
    g_score = {start: 0}  # Стоимость пути от старта
    f_score = {start: heuristic(start, goal)}  # Эвристическая стоимость до цели
    
    # Дополнительный параметр для учета статистики
    probability = {start: 1.0}  # Вероятность для старта (начальная 1)

    
    color_iter=0
    while open_list:
        if color_iter%speed==0:
            draw_list(list(zip(*open_list))[1])
        color_iter+=1
        _, current = heappop(open_list)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        y, x = current
        canvas.itemconfig(maze[y][x].rect_obj, fill=VISITED_COLOR)
        root.update()

        for neighbor in neighbors(x, y, HEIGHT, WIDTH):
            ny, nx = neighbor
            if maze[ny][nx].if_not_wall == 0:  # Если стена, пропускаем
                continue

            tentative_g_score = g_score[current] + 1
            tentative_prob = probability[current] * (1 - maze[ny][nx].if_not_wall)  # Учитываем вероятность

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                g_score[neighbor] = tentative_g_score
                probability[neighbor] = tentative_prob
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_list, (f_score[neighbor], neighbor))
                came_from[neighbor] = current

    return []



def a_star(start, goal, maze):
    """ Реализация алгоритма A* """
    HEIGHT = maze.shape[0]
    WIDTH = maze.shape[1]
    open_list = []
    heappush(open_list, (0, start))
    came_from = {}
    g_score = {start: 0}
    
    
    
    color_iter=0
    while open_list:
        if color_iter%speed==0:
            draw_list(list(zip(*open_list))[1])
        color_iter+=1
        _, current = heappop(open_list)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        y, x = current
        canvas.itemconfig(maze[y][x].rect_obj, fill=VISITED_COLOR)
        root.update()
        
        for neighbor in neighbors(x, y, HEIGHT, WIDTH):
            ny, nx = neighbor
            if maze[ny][nx].if_not_wall == 0:  # Если стена, пропускаем
                continue
            
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_list, (f_score, neighbor))
                came_from[neighbor] = current
               
        
    
    return []



def reconstruct_path(came_from, current):
    """ Восстанавливаем путь по пришедшим координатам """
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def draw_list(lst,color=OPEN_COLOR):
    for (y,x) in lst:
        canvas.itemconfig(maze[y][x].rect_obj, fill=color)
    root.update()

def draw_path(path,P_C=FINAL_COLOR):
    """ Отображаем найденный путь """
    for (y, x) in path:
        if P_C==PATH_COLOR:
            canvas.itemconfig(maze[y][x].rect_obj, fill=P_C)
            root.update()
        else:
            canvas.itemconfig(maze[y][x].rect_obj, fill=P_C)
            root.update()
            
            
def show_popup(text="Уведомление",geometry="200x100+500+300",color='black'):
    # Создаем новое окно поверх основного
    popup = tk.Toplevel()
    popup.title(text)
    popup.geometry(geometry)  # Устанавливаем размер и позицию окна
    popup.overrideredirect(True)  # Убираем рамку и заголовок окна
    
    # Добавляем текст в окно
    label = tk.Label(popup, text=text, font=("Times New Roman", 20), fg=color)
    label.pack(pady=20)
    
    button = tk.Button(root, text="Сохранить лабиринт?", command=save_maze)
    button.pack(pady=10)
    
    
    # Закрытие по нажатии Enter
    popup.bind("<Return>", lambda event: popup.destroy())
    
def show_selected():
    global algorythm
    global maze
    global check_choic
    selected_option = combo.get()
    
    label.config(text=f"Вы выбрали: {selected_option}")
    check_choic = check_choice(file_choice.get())
    if check_choic[0]:
        label.config(text=f"Вы импортировали лабиринт: {file_choice.get()}")
        
        if selected_option in algo_list:
            root.destroy()
            algorythm=selected_option
            
def save_maze():
    global maze
    global try_number
    with open(f"maze_{try_number}.txt", "w") as file:
        for row in maze:
            file.write(" ".join(map(lambda cell: str(cell.if_not_wall), row)) + "\n")
            
def check_choice(txt):
    global WIDTH
    global HEIGHT
    if txt in txts:
        try_maze = []
        with open(txt, "r") as file:
            for line in file:
                row = list(map(float, line.split()))
                try_maze.append(row)
            try_maze = np.array(try_maze)
            return True, scan_maze(try_maze)
            '''try:
                try_maze = np.array(try_maze)
                return True,scan_maze(try_maze)
            except:
                print(try_maze.shape)
                return False, 0'''
    if txt == "Выберите txt файл для импортирования лабиринта":
        return True, generate_maze(minus_wealls, WIDTH, HEIGHT)
##############################################################################################
# Визуализация
##############################################################################################

root = tk.Tk()
root.title('Choose an Algorythm')

combo = ttk.Combobox(root, values=algo_list)
combo.set("a_star")  # Устанавливаем начальное значение
combo.pack(pady=20)

file_choice = ttk.Combobox(root, values=txts)
file_choice.set("Выберите txt файл для импортирования лабиринта")  # Устанавливаем начальное значение
file_choice.pack(pady=20)

button = tk.Button(root, text="Подтвердить выбор", command=show_selected)
button.pack(pady=10)


s = tk.Scale(root,label='s', from_=10, to=1000, orient=tk.HORIZONTAL,digits = 4,resolution =   0.001,var=tk.DoubleVar(value=10) )
s.pack(pady=30)

speed=(s.get())**2

label = tk.Label(root, text="")
label.pack(pady=10)


time.sleep(0.3)
root.mainloop()


    
if algorythm=='a_star':
    # Запуск алгоритма A*
    found = False
    while found!=True:
        
        maze = np.array(check_choic[1])
        HEIGHT = maze.shape[0]
        WIDTH = maze.shape[1]
        end = ( maze.shape[1] - 1,maze.shape[0] - 1)  # Целевая точка 

        
        root = tk.Tk()
        root.title("A* Pathfinding Visualization")

        canvas = tk.Canvas(root, width=maze.shape[1] * CELL_SIZE, height=maze.shape[0] * CELL_SIZE)
        canvas.pack()

        
        
        for i in range(maze.shape[0]):
            for j in range(maze.shape[1]):
                
                color = EMPTY_COLOR if maze[i][j].if_not_wall==1 else WALL_COLOR
                rect = canvas.create_rectangle(j*CELL_SIZE,i  * CELL_SIZE,(j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE,fill=color, outline="gray")
                maze[i][j].rect_obj = rect

        # Обозначаем начальную и конечную точки
        sx, sy = start
        ex, ey = end
        canvas.itemconfig(maze[sy][sx].rect_obj, fill=START_COLOR)
        canvas.itemconfig(maze[ey][ex].rect_obj, fill=END_COLOR)
        path = a_star(start, end, maze)   
        if path:
            draw_path(path)
            show_popup("Путь найден", color='green')
            root.mainloop()
            break
        else:
            found=False
            root.destroy()
            maze = generate_maze(minus_wealls, WIDTH, HEIGHT)
            
elif algorythm == 'b_star':
    # Запуск алгоритма B*
    found = False
    while found != True:
        
        maze = np.array(check_choic[1])
        HEIGHT = maze.shape[0]
        WIDTH = maze.shape[1]
        end = (maze.shape[1] - 1, maze.shape[0] - 1)  # Целевая точка 

        root = tk.Tk()
        root.title("B* Pathfinding Visualization")

        canvas = tk.Canvas(root, width=maze.shape[1] * CELL_SIZE, height=maze.shape[0] * CELL_SIZE)
        canvas.pack()

        for i in range(maze.shape[0]):
            for j in range(maze.shape[1]):
                color = EMPTY_COLOR if maze[i][j].if_not_wall == 1 else WALL_COLOR
                rect = canvas.create_rectangle(j * CELL_SIZE, i * CELL_SIZE, (j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE, fill=color, outline="gray")
                maze[i][j].rect_obj = rect

        # Обозначаем начальную и конечную точки
        sx, sy = start
        ex, ey = end
        canvas.itemconfig(maze[sy][sx].rect_obj, fill=START_COLOR)
        canvas.itemconfig(maze[ey][ex].rect_obj, fill=END_COLOR)

        path = b_star(start, end, maze)  # Используем алгоритм B*
        if path:
            draw_path(path)
            show_popup("Путь найден", color='green')
            root.mainloop()
            break
        else:
            found = False
            root.destroy()
            maze = generate_maze(minus_wealls, WIDTH, HEIGHT)