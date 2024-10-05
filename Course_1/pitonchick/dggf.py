import math
def calculate_lcm(x, y):
    if x > y:
        greater = x
    else:
        greater = y
    while(True):
        if((greater % x == 0) and(greater % y == 0)):
            lcm = greater
            break
        greater += 1
    return lcm
am=[]
bm=[]
for a in range (1,1000):
    for b in range(1,1000):
        f=1
        if a>b and a==(a-b)**2:
            am.append(a)
            bm.append(b)
for i in range(len(am)):
    if bm[i]==(9*(int(math.gcd(am[i],bm[i])))):
        print(am[i], ' ', bm[i])
        print(calculate_lcm(am[i], bm[i]))
