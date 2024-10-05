from itertools import *
def f(x):
    P = (x<=28) and (x>=12)
    Q = (x<=30) and (x>=15)
    A = (x >= a1) and (x<=a2)
    return(P<=A) and ( not Q or A)
ox =[i/4 for i in range (10*4,40*4)]
m=float('inf')
for a1, a2 in combinations(ox,2):
    if all(f(x) for x in ox):
        m=min(m, a2-a1)
print(m)