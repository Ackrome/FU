f=open('27-B_23.txt')
n=int(f.readline())
s={0:0}
for i in range(n):
    p = list(map(int,f.readline().split()))
    sums=[s[j]+k for j in s for k in p]
    s={x%3:x for x in sorted(sums, reverse=0)}
#s[91]=10000000000000000000
s[0]=0
print(max(s.values()))
#print(s[91])