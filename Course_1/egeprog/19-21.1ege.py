def f(s,c,m):
    if (s)<=12:
        return c%2==m%2
    if c==m:
        return 0
    h=[f(s-12,c+1,m),f(s//3,c+1,m)]
    return any(h) if(c+1)%2==m%2 else all(h) #В случае вопроса 19 ставить any(h)
print('\033[1mS  M   ИМЯ\033[0m')
for s in range(13,200):
    for m in range(1,10):
        if f(s,0,m)==1:
            if m%2==0:
                print(s,m,f'\033[32m Vano {m//2}\033[0m')
            else:
                print(s,m,f'\033[31m Peto {1+m//2}\033[0m')
            break