n = int(input())
a=[int(input()) for i in range(n)]
o=[0]*n
for j in range(1,n):
    if (n/j)>=1:
        o[j]=(n-j)
k = [0] * (sum(o))
m=len(k)
for h in range(n):
    for p in range(n):
        for l in range (o[p]):
        k[len(k)]=abs(a[l]-a[l+o.index(p)])
print(o)