f=open('17_9372.txt')
a=[int(i) for i in f]
m=[]
for i in range(len(a)):
    if abs(a[i])%1001==0:
        m.append(abs(a[i]))
j=max(m)
b=[]
for i in range(len(a)-1):
    if (len(str(abs(a[i])))==3 or len(str(abs(a[i+1])))==3):
        if a[i]+a[i+1]>j:
            b.append(a[i]+a[i+1])
print(len(b),min(b))