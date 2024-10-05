f = open('26_6031 (1).txt')
n=int(f.readline())
s=[int(i) for i in f]
s=sorted(s, reverse=True)
k=1
m=s[0]
for i in range(1,len(s)):
    if s[i]+6<=m:
        m=s[i]
        k+=1
print(k,m)