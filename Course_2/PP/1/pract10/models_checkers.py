import collections
###################################################################################################
### Класс клетки поля
###################################################################################################
class Cell():
    def __init__(self, figure,figure_color, X, Y):
        self.figure = figure
        self.figure_color = figure_color # 0 - нет фигуры; 1 - белая фигура; 2 - чёрная фигура
        self.X = X
        self.Y = Y
###################################################################################################
### Классы фигур
###################################################################################################
class shash(Cell):
    def __str__(self):
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        
        eaten=[]
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        new_x=xod_data[2]
        new_y=xod_data[3]
        logic=xod_data[4]
        player = xod_data[5]
        new_pos = tuple([new_x, new_y])
        pos = self.predict([cur_x,cur_y,logic,player])
        eat_pos = self.predict([cur_x,cur_y,logic,player],1)
        
        if player==1:

            if new_pos in eat_pos:
                if logic[new_x][new_y].figure_color==2:
                    if new_y-cur_y>0:
                        if new_x-1 in range(8) and new_y+1 in range(8):
                            if logic[new_x-1][new_y+1].figure_color!=0:
                                return 0,0,[]
                            eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                            logic[new_x-1][new_y+1] = shash('shash', 1, new_x-1, new_y+1)
                            logic[new_x][new_y] = zero('0', 0, new_x, new_y)
                            logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)
                            
                            return 2, logic, [eaten]
                        else:
                            return 0,0,[]
                    elif new_y-cur_y<0:
                        if new_x-1 in range(8) and new_y-1 in range(8):
                            if logic[new_x-1][new_y-1].figure_color!=0:
                                return 0,0,[]
                            eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                            logic[new_x-1][new_y-1] = shash('shash', 1, new_x-1, new_y-1)
                            logic[new_x][new_y] = zero('0', 0, new_x, new_y)
                            logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)
                            
                            return 2, logic, [eaten]
                        else:
                            return 0,0,[]
                    else:
                        return 0,0,[]
                else:
                    return 0, 0, []
                
            elif new_pos in pos:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = shash('shash', 1, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    return 1,logic,[] # <=== 1 - успешно, пешка походила
                else:
                    return 0,0,[] # <=== 0 - не успешно - где-то игрок ошибся!
            else:
                return 0,0,[]  
                 
        if player==2:
            
            if new_pos in eat_pos:
                if logic[new_x][new_y].figure_color==1:
                    if new_y-cur_y>0:
                        if new_x+1 in range(8) and new_y+1 in range(8):
                            if logic[new_x+1][new_y+1].figure_color!=0:
                                return 0,0,[]
                            
                            eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                            logic[new_x+1][new_y+1] = shash('shash', 2, new_x+1, new_y+1)
                            logic[new_x][new_y] = zero('0', 0, new_x, new_y)
                            logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)
                            
                            return 2, logic, [eaten]
                        else:
                            return 0,0,[]
                    elif new_y-cur_y<0:
                        if new_x+1 in range(8) and new_y-1 in range(8):
                            if logic[new_x+1][new_y-1].figure_color!=0:
                                return 0,0,[]
                            
                            eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                            logic[new_x+1][new_y-1] = shash('shash', 2, new_x+1, new_y-1)
                            logic[new_x][new_y] = zero('0', 0, new_x, new_y)
                            logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)
                            
                            return 2, logic, [eaten]
                        else:
                            return 0,0,[]
                    else:
                        return 0,0,[]
                else:
                    return 0, 0, []
    
            elif new_pos in pos:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = shash('shash', 2, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    return 1,logic,[] # <=== 1 - успешно, пешка походила
                else:
                    return 0,0,[] # <=== 0 - не успешно - где-то игрок ошибся!
            else:
                return 0,0,[]
            
    def predict(self,xod_data,eat=0):
        
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        probable_pos = []
        eat_pos=[]
        if player==1:
            # <=== Белая пешка

            if cur_x-1 in range(8) and cur_y-1 in range(8):
                if logic[cur_x-1][cur_y-1].figure_color!=player:
                    
                    if  logic[cur_x-1][cur_y-1].figure!='0':
                        eat_pos.append(tuple([cur_x-1, cur_y-1]))
                    else:
                        probable_pos.append(tuple([cur_x-1, cur_y-1]))
                        
            if cur_x-1 in range(8) and cur_y+1 in range(8):
                if logic[cur_x-1][cur_y+1].figure_color!=player:
                    if  logic[cur_x-1][cur_y+1].figure!='0':
                        eat_pos.append(tuple([cur_x-1, cur_y+1]))
                    else:
                        probable_pos.append(tuple([cur_x-1, cur_y+1]))
            if eat:
                return eat_pos
            return probable_pos   
         
        if player==2:
            
            # <=== Чёрная пешка
            if cur_x+1 in range(8) and cur_y-1 in range(8):
                if logic[cur_x+1][cur_y-1].figure_color!=2:
                    if  logic[cur_x+1][cur_y-1].figure!='0':
                        eat_pos.append(tuple([cur_x+1, cur_y-1]))
                    else:
                        probable_pos.append(tuple([cur_x+1, cur_y-1]))
            if cur_x+1 in range(8) and cur_y+1 in range(8):
                if logic[cur_x+1][cur_y+1].figure_color!=2:
                    if  logic[cur_x+1][cur_y+1].figure!='0':
                        eat_pos.append(tuple([cur_x+1, cur_y+1]))
                    else:
                        probable_pos.append(tuple([cur_x+1, cur_y+1]))
            if eat:
                return eat_pos
            return probable_pos
        return []
###################################################################################################
class zero(Cell):
    def __str__(self):
        if self.figure == '0':
            return str(coder[self.figure+'_'+str(self.figure_color)])
        return str(coder[str(self.figure)+'_'+str(self.figure_color)])
    def move(self,xod_data):
        return 0,0,[]
    def predict(self, xod_data,eat=0):
        return []
###################################################################################################
class dam(Cell):
    def __str__(self):
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        
        eaten=[]
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        new_x=xod_data[2]
        new_y=xod_data[3]
        logic=xod_data[4]
        player = xod_data[5]
        new_pos = tuple([new_x, new_y])
        pos = set()
        pos.update(self.predict([cur_x,cur_y,logic,player]))
        pos.update(self.predict([cur_x,cur_y,logic,player],1))
        
        if new_pos in pos:
            if logic[new_x][new_y].figure_color!=player  and logic[new_x][new_y].figure not in ['king','religionman'] and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = dam('dam', player, new_x, new_y)
                logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = dam('dam', player, new_x, new_y)
                    logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]
    def predict(self,xod_data,eat=0):
        
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        probable_pos_NW = []
        probable_pos_SW = []
        probable_pos_SE = []
        probable_pos_NE = []
        pos_NW=[]
        pos_SW=[]
        pos_SE=[]
        pos_NE=[]
        pos=[]
        eat_pos=[]

        probable_pos_NW.extend([tuple([cur_x-i, cur_y-i]) for i in range(1,8)])
        probable_pos_SW.extend([tuple([cur_x+i, cur_y-i]) for i in range(1,8)])
        probable_pos_SE.extend([tuple([cur_x+i, cur_y+i]) for i in range(1,8)])
        probable_pos_NE.extend([tuple([cur_x-i, cur_y+i]) for i in range(1,8)])
        
        for x in probable_pos_NW:
            if x[0] in range(8) and x[1] in range(8):
                pos_NW.append(x)
        for x in probable_pos_SW:
            if x[0] in range(8) and x[1] in range(8):
                pos_SW.append(x)
        for x in probable_pos_SE:
            if x[0] in range(8) and x[1] in range(8):
                pos_SE.append(x)
        for x in probable_pos_NE:
            if x[0] in range(8) and x[1] in range(8):
                pos_NE.append(x)


        if len(pos_NW)!=0:
            k=0
            for x in range(0,len(pos_NW)):
                if logic[pos_NW[x][0]][pos_NW[x][1]].figure_color==0:
                    pos.append(pos_NW[x])
                elif logic[pos_NW[x][0]][pos_NW[x][1]].figure_color!=player:
                    eat_pos.append(pos_NW[x])
                elif logic[pos_NW[x][0]][pos_NW[x][1]].figure_color==player:
                    k=1
                if k==1:
                    break

        if len(pos_SW)!=0:
            k=0
            for x in range(0,len(pos_SW)):
                if logic[pos_SW[x][0]][pos_SW[x][1]].figure_color==0:
                    pos.append(pos_SW[x])
                    
                elif logic[pos_SW[x][0]][pos_SW[x][1]].figure_color!=player:
                    eat_pos.append(pos_SW[x])
                    
                elif logic[pos_SW[x][0]][pos_SW[x][1]].figure_color==player:
                    k=1
                if k==1:
                    break

        if len(pos_SE)!=0:
            k=0
            for x in range(0,len(pos_SE)):
                if logic[pos_SE[x][0]][pos_SE[x][1]].figure_color==0:
                    pos.append(pos_SE[x])
                elif logic[pos_SE[x][0]][pos_SE[x][1]].figure_color!=player:
                    eat_pos.append(pos_SE[x])
                elif logic[pos_SE[x][0]][pos_SE[x][1]].figure_color==player:
                    k=1
                if k==1:
                    break
        if len(pos_NE)!=0:
            k=0
            for x in range(0,len(pos_NE)):
                if k==1:
                    break
                elif logic[pos_NE[x][0]][pos_NE[x][1]].figure_color==0:
                    pos.append(pos_NE[x])
                elif logic[pos_NE[x][0]][pos_NE[x][1]].figure_color!=player:
                    eat_pos.append(pos_NE[x])
                elif logic[pos_NE[x][0]][pos_NE[x][1]].figure_color==player:
                    k=1
        if eat==1:
            return eat_pos
        return pos
###################################################################################################
### Необходимые переменные
###################################################################################################
Alpha=['A','B','C','D','E','F','G','H']
Beta=['1','2','3','4','5','6','7','8']

figure_classes = {
    'dam': dam,
    '0': zero,
    0: zero,
    'shash':shash
}
coder = {
    'shash_1':'⛀ ',   
    'shash_2':'⛂ ',
    'dam_1'  :'⛁ ',
    'dam_2'  :'⛃ ',
    '0_0':    '  '
}
start_positions = tuple([
    tuple(['0_0','shash_2','0_0','shash_2','0_0','shash_2','0_0','shash_2']),
    tuple(['shash_2','0_0','shash_2','0_0','shash_2','0_0','shash_2','0_0']),
    tuple(['0_0','shash_2','0_0','shash_2','0_0','shash_2','0_0','shash_2']),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['shash_1','0_0','shash_1','0_0','shash_1','0_0','shash_1','0_0']),
    tuple(['0_0','shash_1','0_0','shash_1','0_0','shash_1','0_0','shash_1']),
    tuple(['shash_1','0_0','shash_1','0_0','shash_1','0_0','shash_1','0_0'])
])

'''start_positions = tuple([
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0','0_0','0_0','0_0','dam_2','0_0','0_0','0_0','0_0']),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0','0_0','0_0','dam_1','0_0','0_0','0_0','0_0','0_0']),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
])'''
###################################################################################################
### Класс поля
###################################################################################################
class Field():
    def __init__(self, logic=None):
        self.logic = logic if logic else self.first_generation()

    def first_generation(self):
        logic = [[0 for i in range(8)] for j in range(8)] # <=== Логическое представление игрового поля, его модель

        for i in range(8):
            for j in range(8):
                logic[i][j] = figure_classes[start_positions[i][j][:-2]](figure=start_positions[i][j][:-2],figure_color=int(start_positions[i][j][-1]), X=i, Y=j)

        return logic
    
    def predict_danger(self, logic, play, l=0):
        eat_predict_list = []
        for row in range(8):
            for x in range(8):
                if logic[row][x].figure_color!=play:
                    predictions = logic[row][x].predict([row,x,logic,play+1],1)
                    for i in predictions:
                        if i[0] in [_ for _ in range(8)] and i[1] in [_ for _ in range(8)]:
                            if logic[i[0]][i[1]].figure_color==play:
                                eat_predict_list.append(i)
                    
        return eat_predict_list

                
                
    def render(self, moves, eaten,predictlist=[], eat_predictlist=[],danger_predictlist=[],chekking_list=[],linking_dict=dict()):
        color=(moves)%2+1
        eaten_w=[]
        eaten_b=[]
        for i in range(len(eaten)):
            if eaten[i][-1]=='1':
                eaten_w.append(coder[eaten[i]])
            else:
                eaten_b.append(coder[eaten[i]])

        co_eaten_w=dict(collections.Counter(eaten_w))
        co_eaten_b=dict(collections.Counter(eaten_b))
        if len(predictlist)!=0 or len(eat_predictlist)!=0:
            if color == 1:

                #### Выведем буквы

                print(' '.center(1),end='',)
                for i in range(len(Alpha)):
                    print(('\033[33m'+Alpha[i]+'\033[0m').center(11), end='')
                
                #### Выведем метку для съеденных фигур
                    
                print('\033[33mEaten figures:\033[0m'.center(60))

                #### начнем выводить фигуры

                for row in range(len(self.logic)):
                    for x in range(len(self.logic[row])):
                        if x==0: #### Выведем Цифры
                            print(('\033[33m'+Beta[7-row]+'\033[0m'+' ').center(2), end='')
                        if tuple([row,x]) in predictlist: #### Возможные перемещения без съедания
                            print((f'\033[42m'+str(self.logic[row][x])+'\033[0m').center(11),end='')

                        elif tuple([row,x]) in eat_predictlist:  #### Возможные перемещения со съеданиями
                            print((f'\033[43m'+str(self.logic[row][x])+'\033[0m').center(11),end='')

                        elif tuple([row,x]) in danger_predictlist: #### Фигуры, которые могут быть атакованы
                            print((f'\033[41m'+str(self.logic[row][x])+'\033[0m').center(11),end='')

                        elif tuple([row,x]) in chekking_list: #### Выдeеляет клетки, которые могут атаковать короля
                            print((f'\033[45m'+str(self.logic[row][x])+'\033[0m').center(11),end='')

                        else:  #### Обычнй вывод фигур 
                            print((f'\033[4{7*((1+row+x)%2)}m'+str(self.logic[row][x])+'\033[0m').center(11),end='')

                        if x==len(self.logic[row])-1:
                            print((' \033[33m'+Beta[7-row]+'\033[0m'+' ').center(2), end='')
                            if row == 0:
                                print('\033[1m\033[40m\033[37mWhite\033[0m'.center(40),end='')
                                print('\033[1m\033[47m\033[30mBlack\033[0m'.center(36))
                            else:
                                try:
                                    print((list(co_eaten_w.keys())[row-1] +'x'+str(co_eaten_w[list(co_eaten_w.keys())[row-1]])).center(20),end='')
                                except KeyError:
                                    print(''.center(20),end='')
                                except IndexError:
                                    print(''.center(20),end='')
                                finally:
                                    try:
                                        print((list(co_eaten_b.keys())[row-1] +'x'+str(co_eaten_b[list(co_eaten_b.keys())[row-1]])).center(21),end='')
                                    except KeyError:
                                        print(' ',end='')
                                    except IndexError:
                                        print(' ',end='')
                                    finally:
                                        print()
                print(' '.center(1),end='')
                for i in range(len(Alpha)):
                    print(('\033[33m'+Alpha[i]+'\033[0m').center(11), end='')
                print(f'Moves: {moves}'.center(19),end='')
                print("\033[1m\033[40m\033[37mWhite's move\033[0m".center(20))
            else:
                print(' '.center(1),end='')
                for i in range(len(Alpha)):
                    print(('\033[33m'+Alpha[7- i]+'\033[0m').center(11), end='')
                print('\033[33mEaten figures:\033[0m'.center(60), end='')
                print()
                for row in range(len(self.logic)):
                    for x in range(len(self.logic[row])):
                        if x==0:
                            print(('\033[33m'+Beta[row]+'\033[0m'+' ').center(2), end='')
                        if tuple([7-row,7-x]) in predictlist:
                            print((f'\033[42m'+str(self.logic[7-row][7-x])+'\033[0m').center(11),end='')
                        elif tuple([7-row,7-x]) in eat_predictlist:
                            print((f'\033[43m'+str(self.logic[7-row][7-x])+'\033[0m').center(11),end='')
                        elif tuple([7-row,7-x]) in danger_predictlist:
                            print((f'\033[41m'+str(self.logic[7-row][7-x])+'\033[0m').center(11),end='')
                        elif tuple([7-row,7-x]) in chekking_list:
                            print((f'\033[45m'+str(self.logic[7-row][7-x])+'\033[0m').center(11),end='')
                        #elif tuple([7-row,7-x]) in list(linking_dict.keys()):
                            print((f'\033[46m'+str(self.logic[7-row][7-x])+'\033[0m').center(11),end='')
                        else:
                            print((f'\033[4{7*((1+row+x)%2)}m'+str(self.logic[7-row][7-x])+'\033[0m').center(11),end='')
                        if x==len(self.logic[row])-1:
                            print((' \033[33m'+Beta[row]+'\033[0m'+' ').center(2),end='')
                            if row == 0:
                                print('\033[1m\033[40m\033[37mWhite\033[0m'.center(40),end='')
                                print('\033[1m\033[47m\033[30mBlack\033[0m'.center(36))
                            else:
                                try:
                                    print((list(co_eaten_w.keys())[row-1] +'x'+str(co_eaten_w[list(co_eaten_w.keys())[row-1]])).center(20),end='')
                                except KeyError:
                                    print(''.center(20),end='')
                                except IndexError:
                                    print(''.center(20),end='')
                                finally:
                                    try:
                                        print((list(co_eaten_b.keys())[row-1] +'x'+str(co_eaten_b[list(co_eaten_b.keys())[row-1]])).center(21),end='')
                                    except KeyError:
                                        print(' ',end='')
                                    except IndexError:
                                        print(' ',end='')
                                    finally:
                                        print()
                print(' '.center(1),end='')
                for i in range(len(Alpha)):
                    print(('\033[33m'+Alpha[7-i]+'\033[0m').center(11), end='')
                print(f'Moves: {moves}'.center(19),end='')
                print("\033[1m\033[47m\033[30mBlack's move\033[0m".center(20))
