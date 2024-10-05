f=open('27B_1977.txt')
n=int(f.readline())
ms=0
mk=0
msu=[10**20]*43
mku=[10**20]*43
s=0
k=0
for i in range(n):
    x = int(f.readline())
    s+=x
    k+=1
    if s%43==0:
        ms=s
        mk=i+1
    s1=s-msu[s%43]
    k1=i+1-mku[s%43]
    if (k1<mk and s1==ms) or (s1>ms):
        ms=s1
        mk=k1
    if s<msu[s%43]:
        msu[s%43]=s
        mku[s%43]=i+1
print(mk)