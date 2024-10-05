f=[1]*12000
for i in range(0,11000,2):
     f[i] = f[i+2] - 3
print(f[80])