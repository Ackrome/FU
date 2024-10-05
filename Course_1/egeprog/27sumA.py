f=open('27-A_23 (1).txt')
n=int(f.readline())
s={0}
for i in range(n):
    a=set()
    x,y= list(map(int, f.readline().split()))
    for j in s:
        a.add(j+x)
        a.add(j+y)
        #a.add(j + z)
    s=a
s1=[x for x in s if x%3!=0]
print(max(s1))
