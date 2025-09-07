import numpy as np
###############################################################################
####### Нужные функции
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
def check_convex_polygon(polylist):
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
def check_polygon_angles_inside(polylist,checkpol):
    '''Проверяет, имееет ли фигура любой из углов заданного многоугольника и является ли она выпуклым многоугольником'''
    if not check_convex_polygon(polylist):
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
#######Декораторы фильтрации вывода
###############################################################################
def flt_convex_polygon(func):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            newrows=[]
            for _ in row:
                polylist = _
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
                
                if flag:
                    newrows.append(_)
            if len(newrows):
                newnewrows.append(newrows)
        result = func(*newnewrows,**kwargs)
        
        return result
    
    return wrapper
###############################################################################
def flt_angle_point(func,cordinates:tuple):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            newrows=[]
            for _ in row:
                polylist = _
                flag = False
                for i in range(len(polylist)):
                    a=polylist[i]
                    if a == cordinates:
                        flag = True
                        break
                if flag:
                    newrows.append(_)
            if len(newrows):
                newnewrows.append(newrows)
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def flt_square(func,square):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            newrows=[]
            for _ in row:
                polylist = _
                flag = True
                s = find_surface(polylist)
                if s <= square:
                    flag = False
                    
                if flag:
                    newrows.append(_)
            if len(newrows):
                newnewrows.append(newrows)
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def flt_short_side(func,side):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            newrows=[]
            for _ in row:
                polylist = _
                flag = True
                s = find_sides(polylist)
                if min(s) <= side:
                    flag = False
                    
                if flag:
                    newrows.append(_)
            if len(newrows):
                newnewrows.append(newrows)
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def flt_point_inside(func,cors:tuple):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            newrows=[]
            for _ in row:
                polylist = _
                if check_convex_polygon(polylist):
                    x,y = cors
                    xp,yp=list(zip(*polylist))
                    c=0
                    for i in range(len(xp)):
                        if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): 
                            c = 1 - c    
                    
                    if not c:
                        newrows.append(_)
            
            if len(newrows):
                newnewrows.append(newrows)
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def flt_polygon_angles_inside(func,checkpol):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            
            newrows=[]
            for _ in row:
                if check_polygon_angles_inside(_,checkpol):
                    newrows.append(_)
            
            if len(newrows):
                newnewrows.append(newrows)
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
#######Декораторы изменения вывода
###############################################################################
def tr_translate(func, tox = 0,toy=0):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            
            newrows=[]
            for _ in row:
                
                loadin = []         
                for i in range(len(_)):
                    
                    u = list(_[i])
                    u[1]+=toy
                    u[0]+=tox
                            
                    loadin.append(tuple(u))
                loadin=tuple(loadin)
                newrows.append(loadin)
                
            newnewrows.append(newrows)     
                         
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def tr_rotate(func,degrees=0,center=(0,0)):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            
            newrows=[]
            for _ in row:
                rad = degrees*np.pi/180
                loadin = []         
                for i in range(len(_)):
                
                    u = list(_[i])
                    unew = (center[0] + (u[0]-center[0])*np.cos(rad)-(u[1]-center[1])*np.sin(rad),center[1]+(u[0]-center[0])*np.sin(rad)+(u[1]-center[1])*np.cos(rad))
                    
                    loadin.append(unew)
                loadin=tuple(loadin)
                newrows.append(loadin)
                
            newnewrows.append(newrows)     
                         
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def tr_homothety(func,k=-1,center=(0,0)):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            
            newrows=[]
            for _ in row:
                loadin = []         
                for i in range(len(_)):
                    u = list(_[i])
                    unew = (center[0]+k*(u[0]-center[0]),center[1]+k*(u[1]-center[1]))
                    loadin.append(unew)
                loadin=tuple(loadin)   
                newrows.append(loadin)
                
            newnewrows.append(newrows)     
                         
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper
###############################################################################
def tr_symmetry(func,k,b):
    
    def wrapper(*rows,**kwargs):
        
        newnewrows = []
        for row in rows:
            
            newrows=[]
            for _ in row:
                loadin = []
                if len(_):      
                    for i in range(len(_)):
                        a = list(_[i])
                        unew = (2*(a[0]-k*(b-a[1]))/(1+k**2) - a[0],(k*(2*a[0]+k*a[1])+2*b-a[1])/(1+k**2))
                        loadin.append(unew)
                    loadin=tuple(loadin)
     
                newrows.append(loadin)
                
            newnewrows.append(newrows)     
                         
        result = func(*newnewrows,**kwargs)
        
        return result

    return wrapper