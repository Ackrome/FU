from fnmatch import *
def f(x):
    for i in range(2,int(x**0.5)+1):
        if x%i==0:
            return False
    return True
def r(x):
    m=set()
    for i in range(2,int(x**0.5)+1):
        if x%i==0:
            m.add(i)
            m.add(x//i)
    if len(m)<2:
        return 0
    else:
        return sorted(m)[0]+sorted(m)[1]
j=0
for i in range(1200000):
    if r(i)>0 and r(i)%2022==0:
        b.append(i,r(i))

    if j==5:
        break