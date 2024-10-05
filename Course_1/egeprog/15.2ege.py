m=[]
for a in range (1,1000):
    flag = 0
    for x in range(1000):
        if ((x%10==0) and (x%26==0) and ((x>=300)<=(a<=x)))==False:
            flag =1
    if flag==0:
        print(a)
