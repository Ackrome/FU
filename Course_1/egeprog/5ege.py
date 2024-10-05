def inv(n):
    new=''
    for x in range(0, len(n)):
        new += '0' if int(n[x]) else '1'
    return new
l=[]
m=[]
for n in range(10000):
    b=bin(n)[2:]
    if n%3==0:
        b+=b[:2]
    else:
        b+=bin((n%3))[2:]
    r=int(b,2)
    if r<105:
        m.append(r)
        l.append(n)
print(l[m.index(max(m))])