from fnmatch import *
def f(x):
    m=set()
    for i in range(2,int(x**0.5)+1):
        if x%i==0:
            m.add(i)
            m.add(x//i)
    return m
for i in range(1,10**7,1):
        if fnmatch(str(i),'3*52?') and len(f(i))%2!=0:
            print(i,max(f(i)))

