slovo = input()
chet=0
for char in slovo:
    if char!='H' and char!='O' and char!='N' and char!='I':
        slovo = slovo.replace(char, '',1)
for char2 in slovo:
        if 'HH' in slovo:
            slovo=slovo.replace('HH','H',1)
        if 'OO' in slovo:
            slovo=slovo.replace('OO','O',1)
        if 'NN' in slovo:
            slovo= slovo.replace('NN', 'N', 1)
        if 'II' in slovo:
            slovo = slovo.replace('II', 'I', 1)
        if 'HONI' in slovo:
            slovo=slovo.replace('HONI','',1)
            chet=chet+1
print(chet)