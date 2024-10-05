def r(x):
    m=set()
    for i in range (2,int(x**0.5)+1):
        if x%i==0:
            m.add(i)
            m.add(x//i)
    return sorted(m)
for i in range(350301,351301):
    if sum(r(i))%13==0:
        print(i,sum(r(i))//13)


