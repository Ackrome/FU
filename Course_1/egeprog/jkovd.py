f=open('27A_7879.txt')
n=int(f.readline())
k=int(f.readline())
a=[int(i) for i in f]
b=[]
m=[]
for i in range(n):
    for j in range(i+1,n):
        if j-i>=k:
            s=a[i]+a[j]
            if s%2023==0:
                if ((a[i]%47==0 and a[j]%47!=0) or (a[i]%47!=0 and a[j]%47==0)):
                    b.append(s)
print(max(b))
