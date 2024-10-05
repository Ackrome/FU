def sumcifr(n):
    k=0
    while n>0:
        k+=n%10
        n=n//10
    return k
for n in range(3,1000):
    j='3'+n*'5'
    while '555' in j or '355' in j or '25' in j:
        if '25' in j:
            j=j.replace('25','32',1)
        if '355' in j:
            j=j.replace('355','25',1)
        if '555' in j:
            j=j.replace('555','3',1)
    if sumcifr(int(j))==17 :
        print(n)
