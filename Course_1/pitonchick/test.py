n = input()
l=n.split('|')
for i in range(0,len(l)):
    l[i]=l[i][0]
C= l.count('C') + l.count('F')+  l.count('G')
A= l.count('A') + l.count('D')+  l.count('E')
if C>A:
    print('C-dur')
elif C<A:
    print('A-dur')
elif C==A:
    if l[len(l)-1]=='A' or l[len(l)-1]=='C':
        print(f'{l[len(l) - 1]}-dur')
    else:
        if l[len(l) - 2] == 'A' or l[len(l) - 2] == 'C':
            print(f'{l[len(l) - 2]}-dur')
        else:
            if l[len(l) - 3] == 'A' or l[len(l) - 3] == 'C':
                print(f'{l[len(l) - 3]}-dur')
