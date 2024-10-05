s=55*'2' +44*'3' +33*'1'
while '222' in s or '333' in s or '111' in s:
    if '222' in s:
        s = s.replace('222','11',1)
        if '222' in s:
            s = s[::-1]
            s = s.replace('222','11',1)
            s = s[::-1]
    elif '111' in s:
        s = s.replace('111', '3', 1)
    else:
        s = s.replace('333', '1', 1)
print(s)