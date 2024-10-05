def g(a):
    m=set()
    for i in range(2,(int(a**0.5)+1)):
        if a%i==0:
            m.add(i)
            m.add(a//i)
    if len(m)==0:
        return True
    else:
        return False
def f(a,b):
    if a>b or g(a)==1:
        return 0
    if a==b:
        return 1
    if a<b:
        return f(a+1,b)+f(a+2,b)+f(a*3,b)
print(f(8,16)*f(16,32))
