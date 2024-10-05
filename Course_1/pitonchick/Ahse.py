n=int(input())
l=list()
for i in range(n):
    l.append(input())
a=[]
b=[]
for i in range(n):
    a.append(int(l[i][0]))
    b.append(int(l[i][2]))
flag=[0]*5
nch=[]

for i in range(n):
    if (i+1)==n:
        break
    if a[i]<b[i]:
        if a[i]==a[i+1] or a[i]==b[i+1]:
            flag[a[i]-1]=flag[a[i]-1]+1
        elif b[i]==a[i+1] or b[i]==b[i+1]:
            flag[b[i]-1] = flag[b[i]-1] + 1
    else:
        if b[i]==a[i+1] or b[i]==b[i+1]:
            flag[b[i]-1] = flag[b[i]-1] + 1
        elif a[i]==a[i+1] or a[i]==b[i+1]:
            flag[a[i]-1]=flag[a[i]-1]+1
print(max(flag)+1,flag.index(max(flag))+1)




