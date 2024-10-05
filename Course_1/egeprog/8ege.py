m=[]
k=0
for a in '2468':
    for b in '012345678':
        for c in '012345678':
            for d in '012345678':
                for e in '0234567':
                    s = a + b + c + d + e
                    if s.count('3')<=1:
                        k += 1
print(k)



