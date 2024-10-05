def f(a,b,c,m):
    if (a+b)>=255:
        return c%2==m%2
    if c==m:
        return 0
    h=[f(a,b+1,c+1,m),f(a,b*2,c+1,m),f(a+1,b,c+1,m),f(a*2,b,c+1,m)]
    return any(h) if(c+1)%2==m%2 else all(h) #В случае вопроса 19 ставить any(h)
print('\033[1mS  M   ИМЯ\033[0m')
for b in range(1,237):
    for m in range(1,10):
        if f(17,b,0,m)==1:
            if m%2==0:
                print(b,m,f'\033[32m Vano {m//2}\033[0m')
            else:
                print(b,m,f'\033[31m Peto {1+m//2}\033[0m')
            break