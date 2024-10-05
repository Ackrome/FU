f=open('27B_2901.txt')
n=int(f.readline())
m=[0]*666
s=0
k=0
for i in range(n):
    x=int(f.readline())
    s+=x
    if s%666==0:
        k+=1
    k+=m[s%666]
    m[s%666]+=1
print(k)