a=[]
for x in range(-2,4):
    for y in range(-2,4):
        if x==0 or y==0 or (abs(x)+abs(y))!=5:
            continue
        a.append((x,y))
print(set(a))

b=[(x,y) for x in range(-3,4) for y in range(-3,4) if not(x==0 or y==0 or (abs(x)+abs(y))!=5)]
print(set(b))
