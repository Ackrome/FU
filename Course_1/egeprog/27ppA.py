f=open('27-A_23 (1).txt')
n=int(f.readline())
a=[int(i) for i in f]
ms=0
mk=0
for i in range(n):
    k = 0
    s=0
    for j in range(i,n):
        s+=a[j]
        k += 1
        if s%43==0:
            if s>ms or (s==ms and k<mk):
                ms=s
                mk=k
print(mk)