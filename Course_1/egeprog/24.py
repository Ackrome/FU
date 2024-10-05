f=open('24_4710.txt').readline()
f=f.replace('O', 'A').replace('C','F')...
c=f.split()
print(len(max(c,key=len)))