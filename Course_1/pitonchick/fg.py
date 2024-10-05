def hg(n,k):
    a=str('')
    for i in range(n):
        if a.count(' ' + str(i + 1)) == 0:
            a = a + ' ' + str(i + 1)
    al = a.split(' ')
    al.remove('')
    for f in range(k):
        al.remove(str(f + 1))
    for i in range(len(al)):
        al[i]=int(al[i])
    return sum(al)
her=[]
for j in range(1,28):
    her.append(hg((j-1)**2 + 2 * j - 1, (j-1)**2))
print(her)
