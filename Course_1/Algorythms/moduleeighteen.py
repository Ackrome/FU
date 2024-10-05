def circle_s_r(r):
    '''Площадь круга  от радиуса'''
    if type(r)!=int:
        raise TypeError('Неправильный ввод!')
    return 3.14*r**2

def circle_s_d(d):
    '''Площадь круга  от диаметра'''
    if type(d)!=int:
        raise TypeError('Неправильный ввод!')
    return 3.14*(d**2)/4

def circle_l_r(r):
    '''Длина окружности от радиуса'''
    if type(r)!=int:
        raise TypeError('Неправильный ввод!')
    return 2*3.14*r

def circle_l_d(d):
    '''Длина окружности от диаметра'''
    if type(d)!=int:
        raise TypeError('Неправильный ввод!')
    return 3.14*d

def circle_sector_s_r(r,a):
    '''Площадь сектора круга  от радиуса r и угла a'''
    if type(r)!=int or type(a)!=int or a not in[int(i) for i in range(361)]:
        raise TypeError('Неправильный ввод!')
    return (3.14*r**2)*a/360

def circle_sector_s_d(d,a):
    '''Площадь сектора круга  от диаметра d и угла a'''
    if type(d)!=int or type(a)!=int or a not in[int(i) for i in range(361)]:
        raise TypeError('Неправильный ввод!')
    return (3.14*d**2)*a/(360*4)

def squareincircle_p_r(r):
    '''Периметр вписанного в окружность квадрата от радиуса'''
    if type(r)!=int:
        raise TypeError('Неправильный ввод!')
    return 4*r*2**0.5

def squareincircle_p_d(d):
    '''Периметр вписанного в окружность квадрата от диаметра'''
    if type(d)!=int:
        raise TypeError('Неправильный ввод!')
    return 2*d*2**0.5
