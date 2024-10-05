import random as rn
def gen_matrixes_file(n,m,file_name='text'):
    file = open((file_name + '.txt'), 'a')
    lines=[]

    all_values=[rn.randint(-100,100) for i in range(m*n)]
    p=len(str(max(all_values))) + 2
    for i in range(len(all_values)):
        if str(all_values[i])[0]=='-':
            all_values[i]=(str(all_values[i])+' '*(p+1-len(str(all_values[i]))))
        else:
            all_values[i]=(' '+str(all_values[i])+' '*(p-len(str(all_values[i]))))

    for j in range(m):
        klo = ''
        for i in range(n):
            klo+=str(all_values[j*n+i])
    lines.append(klo+'\n')

  #Разделим матрицы пустой строкой

    lines.append('\n')

    file.writelines(lines)

gen_matrixes_file(2,2,'21')
