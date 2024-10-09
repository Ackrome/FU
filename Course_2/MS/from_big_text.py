import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def from_big_text(data:str,splitter:str):
    
    index = pd.Index('''Объем выборки до удаления пропущенных данных
Количество пропущенных данных (NA)
Объем выборки после удаления пропущенных данных
Минимальное значение в вариационном ряду
Максимальное значение в вариационном ряду
Размах выборки
Значение первой квартили (Q1)
Значение медианы (Q2)
Значение третьей квартили (Q3)
Квартильный размах
Среднее выборочное значение
Стандартное отклонение (S) корень из дисп.в (исправленной)
Исправленная дисперсия 
Эксцесс
Коэффициент асимметрии
Ошибка выборки
Значение 63%-квантили
Мода
Как часто встречается "мода"
Верхняя граница нормы (Xst_max)
Нижняя граница нормы (Xst_min)
Количество выбросов ниже нижней нормы
Количество выбросов выше верхней нормы
'''.split('\n'))
    
    data_list=[]
    df=pd.DataFrame([float(i) if i!='NA' else np.nan for i in data.split(splitter)])
    
    length_before=df.size
    data_list.append(length_before)
    
    df=df.dropna()
    length_after=df.size
    data_list.extend([length_after-length_before,length_after])
    
    minn=df.describe().loc['min'].values[0]
    maxx=df.describe().loc['max'].values[0]
    data_list.extend([minn,maxx,maxx-minn])
    
    Q1=df.describe().loc['25%'].values[0]
    Q2=df.describe().loc['50%'].values[0]
    Q3=df.describe().loc['75%'].values[0]
    
    mean = df.describe().loc['mean'].values[0]
    
    data_list.extend([Q1,Q2,Q3,Q3-Q1,mean,df.std(ddof=1)[0],df.var(ddof=1)[0],df.kurt()[0],df.skew()[0]])
    
    data_list.append(data_list[11]/data_list[2]**0.5)
    data_list.extend(df.quantile(0.63))
    
    if df.mode().count()[0] == df.count().iloc[0]:
        data_list.append(0)
        data_list.append(0)
    else:
        data_list.append(df.mode().iloc[0,0])
        data_list.append(df.value_counts()[df.mode().iloc[0,0]])
        
    data_list.extend([data_list[8]+1.5*data_list[9],data_list[6]-1.5*data_list[9]])
    data_list.extend([len(df[df.iloc[:,0]<data_list[20]]),len(df[df.iloc[:,0]>data_list[19]])])
    
    df.boxplot()
    plt.xlabel('Ящик с усами до очистки')
    plt.show()

    clean_df=df[(df.iloc[:,0]>data_list[20]) & (df.iloc[:,0]<data_list[19])]
    clean_df.boxplot()
    plt.xlabel('Ящик с усами после очистки (Без NA и выбросов)')
    plt.show()
    
    
    return pd.DataFrame(data_list,index[:len(data_list)])