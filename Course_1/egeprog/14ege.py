def prost(c):
    for i in range(2,c):
        if c%i==0:
            return False
    return True
m=[]
for x in '0123456789abcdef':
    for y in '0123456789abcdef':
        if (int('27a'+x+'23',16)+int('8'+y+'e5d2',16))%5==0:
            m.append(int(x+y,16))
print(max(m))