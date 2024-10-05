def sem(i):
    m = []
    for n in range(9999,i):
        s = ''
        while n > 0:
            s = str(n % 7) + s
            n = n // 7
        if s.count('5') == 1:
           h=[s.count('50') == 0, s.count('52') == 0, s.count('54') == 0, s.count('56') == 0, s.count('05') == 0,s.count('25') == 0, s.count('45') == 0, s.count('65') == 0]
           if all(h) == True:
                m.append(1)
    return sum(m)
print(sem(100000))