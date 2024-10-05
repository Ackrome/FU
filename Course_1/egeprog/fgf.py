f = open('26_2613.txt')
s=[int(i) for i in f]
s=sorted(s, reverse= 1)
a=[]
while len(s)>0:
    b=[]
    for i in range(len(s)):
        if len(b)==0 or (b[-1]-s[i])>=11:
            b.append(s[i])
            s[i]=0
    a.append(len(b))
    s=[int(i) for i in s if i!=0]
print(max(a),len(a))