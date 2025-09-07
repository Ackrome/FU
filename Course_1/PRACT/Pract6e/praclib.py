import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon,Circle

###############################################################################
####### Вывод поля
###############################################################################
def draw_field(*rows,color=0,ecolor = 'black',figdpi=100,enlarge=0,show_axises=True,radius=0.1, grid=True, show_x=True,show_y=True):
    '''Вывод поля'''
    max_x = max_y = -float('inf')
    min_x = min_y = float('inf')
    
    canvas, axis = plt.subplots()
    
    axis.set_axisbelow(True)
    
    if show_axises:
        axis.axhline(y=0, color='r', alpha=0.35)
        axis.axvline(x=0, color='r', alpha=0.35)
        
    if grid:    
        axis.grid(color='gray', linestyle='dashed')
        
    canvas.dpi=figdpi
    
    for field in rows:
        for fig in field:

            for x, y in fig:
                max_x = max(x, max_x)
                max_y = max(y, max_y)
                min_x = min(x, min_x)
                min_y = min(y, min_y)
            if len(fig)==1 and color:
                p = Circle(*fig,radius=radius,edgecolor=ecolor , facecolor=color)
            elif len(fig)==1:
                p = Circle(*fig,radius=radius,edgecolor=ecolor,fill=False)
            elif color:   
                p = Polygon(fig,edgecolor=ecolor , facecolor=color)
            else:
                p = Polygon(fig,edgecolor=ecolor ,fill=False)
            axis.add_patch(p)
            
    if not show_x:
        axis.get_xaxis().set_visible(False)
    if not show_y:
        axis.get_yaxis().set_visible(False)
   
    
    axis.set_xlim([min_x-enlarge, max_x+enlarge])
    axis.set_ylim([min_y-enlarge, max_y+enlarge])
    
    axis.set_aspect(1)
    return axis
###############################################################################
####### Координаты простейших полигонов
###############################################################################
def triangle_cors(x,y,storona):
    '''Координаты треугольника'''
    return (
        (x,y),
        (x+storona, y),
        (x+storona/2, y+storona*3**0.5/2)
    )
###############################################################################    
def square_cors(x,y,storona):
    '''Координаты Квадрата'''
    return (
        (x,y),
        (x+storona, y),
        (x+storona, y+storona),
        (x, y+storona)
    )
###############################################################################        
def rectangle_cors(x,y,storona1,storona2):
    '''Координаты прямоугольника'''
    return (
        (x,y),
        (x+storona1, y),
        (x+storona1, y+storona2),
        (x, y+storona2)
    )
###############################################################################    
def hexagon_cors(x,y,storona):
    '''Координаты шестиугольника'''
    return (
        (x,y),
        (x+storona, y),
        (x+storona*3/2, y+storona*3**0.5/2),
        (x+storona, y+storona*3**0.5),
        (x, y+storona*3**0.5),
        (x-storona/2, y+storona*3**0.5/2)
    )
###############################################################################
#######Генерация кортежей лент простейших полигонов
###############################################################################
def gen_triangle(n=1,x=0,y=0,storona=2,mezhdu=0):
    '''Генерация ленты треугольников'''
    j=[]
    for i in range(n):
        j.append(triangle_cors(x+i*(storona + mezhdu),y,storona))
    return j
###############################################################################
def gen_hexagon(n=1,x=0,y=0,storona=2,mezhdu=0):
    '''Генерация ленты шестиугольников'''
    j=[]
    for i in range(n):
        j.append(hexagon_cors(x+2*i*(storona)+i*mezhdu,y,storona))
    return j
###############################################################################
def gen_rectangle(n=1,x=0,y=0,storona1=2,storona2=2,mezhdu=0):
    '''Генерация ленты прямоугольников'''
    j=[]
    for i in range(n):
        j.append(rectangle_cors(x+i*(storona1 + mezhdu),y,storona1,storona2))
    return j
###############################################################################
#######Функции для map()
###############################################################################
def tr_translate(polylist, tox = 0,toy=0):
    '''Параллельный перенос'''
    loadin = []         
    for i in range(len(polylist)):
    
        u = list(polylist[i])
        u[1]+=toy
        u[0]+=tox
            
        loadin.append(tuple(u))
    loadin=tuple(loadin)                    
    return loadin
###############################################################################
def tr_rotate(polylist=[],degrees=0,center=(0,0)):
    '''Поворот'''
    rad = degrees*np.pi/180
    loadin = []         
    for i in range(len(polylist)):
    
        u = list(polylist[i])
        unew = (center[0] + (u[0]-center[0])*np.cos(rad)-(u[1]-center[1])*np.sin(rad),center[1]+(u[0]-center[0])*np.sin(rad)+(u[1]-center[1])*np.cos(rad))
        
        loadin.append(unew)
    loadin=tuple(loadin)                    
    return loadin
###############################################################################
def tr_homothety(polylist=[],k=-1,center=(0,0)):
    '''Гомотетия'''
    loadin = []         
    for i in range(len(polylist)):
        u = list(polylist[i])
        unew = (center[0]+k*(u[0]-center[0]),center[1]+k*(u[1]-center[1]))
        loadin.append(unew)
    loadin=tuple(loadin)                    
    return loadin
###############################################################################
def tr_symmetry(polylist,k,b):
    '''Симметрия относительно прямой y = bx+k'''
    loadin = []
    if len(polylist):      
        for i in range(len(polylist)):
            a = list(polylist[i])
            unew = (2*(a[0]-k*(b-a[1]))/(1+k**2) - a[0],(k*(2*a[0]+k*a[1])+2*b-a[1])/(1+k**2))
            loadin.append(unew)
        loadin=tuple(loadin)
                     
    return loadin
###############################################################################
def find_all_cos(polylist):
    '''Поиск косинусов всех углов многоугольника по координатам'''
    lst = []
    prevlist = polylist
    polylist = polylist + polylist
    for i in range(len(prevlist)):
        a,b,c = polylist[i:i+3]    
        A = ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
        B = ((c[1]-b[1])**2+(c[0]-b[0])**2)**0.5
        C = ((a[0]-c[0])**2+(a[1]-c[1])**2)**0.5
        cosinus = (A**2+B**2+C**2)/(2*A*B)
        lst.append(cosinus)
    return lst
###############################################################################
def find_all_sin(polylist):
    '''Поиск синусов всех углов многоугольника по координатам'''
    lst = []
    prevlist = polylist
    polylist = polylist + polylist
    for i in range(len(prevlist)):
        a,b,c = polylist[i:i+3]
        A = ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
        B = ((c[1]-b[1])**2+(c[0]-b[0])**2)**0.5
        scalAB=(a[0]-b[0])*(c[0]-b[0])+(a[1]-b[1])*(c[1]-b[1])
        sinus = scalAB/(A*B)
        lst.append(sinus)
    return lst
###############################################################################
def find_surface(polylist):
    '''Находит площадь фигуры'''
    s = 0
    prevlist = polylist
    polylist = polylist + polylist
    for i in range(len(prevlist)):
        a,b = polylist[i:i+2]      
        s+=a[0]*b[1] - a[1]*b[0]
    return abs(0.5*s)
###############################################################################
def find_sides(polylist):
    '''Находит длины всех сторон фигуры'''
    slist = []
    prevlist = polylist
    polylist = polylist + polylist
    for i in range(len(prevlist)):
        s=0
        a,b = polylist[i:i+2]
        for j in range(len(a)):
            s+=(a[j]-b[j])**2
        slist.append(s**0.5)
    return slist
###############################################################################
####### Функции для filter()
###############################################################################
def flt_convex_polygon(polylist):
    '''Проверяет, является ли выпуклым многоугольник по его координатам'''
    flag = True
    lst = []
    prevlist = polylist
    polylist = polylist + polylist
    for i in range(len(prevlist)):
        a,b,c = polylist[i:i+3]      
        psev_scalAB=(a[0]-b[0])*(c[1]-b[1])-(a[1]-b[1])*(c[0]-b[0])
        lst.append(psev_scalAB)

    if len(list(filter(lambda x:x>=0,lst)))!=0 and len(list(filter(lambda x:x<=0,lst)))!=0 :
        flag=False
    return flag
###############################################################################
def flt_angle_point(polylist,cordinates:tuple):
    '''Проверяет, имееет ли фигура хотя бы один угол, совпадающий с заданной точкой'''
    flag = False
    for i in range(len(polylist)):
        a=polylist[i]
        if a == cordinates:
            flag = True
            break
    return flag
###############################################################################
def flt_square(polylist,square):
    '''Проверяет, имееет ли фигура площадь меньше заданной'''
    flag = True
    s = find_surface(polylist)
    if s <= square:
        flag = False
    return flag
###############################################################################
def flt_short_side(polylist,side):
    '''Проверяет, имееет ли фигура кратчайшую cторону меньше заданной'''
    flag = True
    s = find_sides(polylist)
    if min(s) <= side:
        flag = False
    return flag
###############################################################################
def flt_point_inside(polylist,cors:tuple):
    '''Проверяет, имееет ли фигура данную точку и является ли она выпуклым многоугольником'''
    if not flt_convex_polygon(polylist):
        return False
    x,y = cors
    xp,yp=list(zip(*polylist))
    c=0
    for i in range(len(xp)):
        if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): 
            c = 1 - c    
    return  not c
###############################################################################
def flt_polygon_angles_inside(polylist,checkpol):
    '''Проверяет, имееет ли фигура любой из углов заданного многоугольника и является ли она выпуклым многоугольником'''
    if not flt_convex_polygon(polylist):
        return False
    xp,yp=list(zip(*polylist))
    clist=[]
    for _ in range(len(checkpol)):
        c=0
        x,y = checkpol[_]
        for i in range(len(xp)):
            if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): 
                c = 1 - c    
        clist.append(not c)
    return any(clist)
###############################################################################
####### Функции для functools.reduce()
###############################################################################        
def agr_origin_nearest(polylist,next_polylist):
    '''Поиск угла, самого близкого к началу координат с помощью functools.reduce()'''
    if str(type(polylist))[8:-2]!='tuple':
        polydict = dict(list(zip([(polylist[0]**2+polylist[1]**2)**0.5]+[(_[0]**2+_[1]**2)**0.5 for _ in next_polylist],[polylist]+list(next_polylist))))
        return list(polydict[min((polylist[0]**2+polylist[1]**2)**0.5,min([(_[0]**2+_[1]**2)**0.5 for _ in next_polylist]))])
    
    polydict = dict(list(zip([(_[0]**2+_[1]**2)**0.5 for _ in polylist]+[(_[0]**2+_[1]**2)**0.5 for _ in next_polylist],polylist+next_polylist)))
    return list(polydict[min(min([(polylist[_][0]**2+polylist[_][1]**2)**0.5 for _ in range(len(polylist))]),min([(_[0]**2+_[1]**2)**0.5 for _ in next_polylist]))])
###############################################################################
def agr_max_side(polylist,next_polylist):
    '''Поиск самого длинной стороны многоугольника с помощью functools.reduce()'''

    polydict = dict(list(zip(find_sides(polylist)+find_sides(next_polylist),[tuple((((polylist+polylist)[i]),((polylist+polylist)[i+1]))) for i in range(len(polylist))]+[tuple((((next_polylist+next_polylist)[i]),((next_polylist+next_polylist)[i+1]))) for i in range(len(next_polylist))])))
    return list(polydict[max(find_sides(polylist)+find_sides(next_polylist))])
###############################################################################
def agr_min_area(polylist,next_polylist):
    '''Поиск самой маленькой площади многоугольника с помощью functools.reduce()'''

    polydict = dict(list(zip([find_surface(polylist),find_surface(next_polylist)],[polylist]+[next_polylist])))
    return list(polydict[min([find_surface(polylist),find_surface(next_polylist)])])   
###############################################################################
def agr_perimeter(polylist,next_polylist):
    '''Расчет суммарного периметра многоугольника с помощью functools.reduce()'''
    return sum(find_sides(polylist)+find_sides(next_polylist)) if str(type(polylist))[8:-2]=='tuple' else polylist+sum(find_sides(next_polylist))
###############################################################################
def agr_area(polylist,next_polylist):
    '''Расчет суммарной площади многоугольника с помощью functools.reduce()'''
    return find_surface(polylist)+find_surface(next_polylist) if str(type(polylist))[8:-2]=='tuple' else polylist+find_surface(next_polylist)

        