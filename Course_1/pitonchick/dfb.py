k=0
for n in range (100000):
    if n%10==5:
        if n<=(15*(1+16+16**2+16**3+16**4+16**5+16**6+16**7) and n>(7*(1+7+7**2+7**2+7**3+7**4+7**5+7**6+7**7+7**8+7**9))):
            k+=1
print(k)
