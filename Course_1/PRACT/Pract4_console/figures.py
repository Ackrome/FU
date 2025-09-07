from models import Cell,Field

coder = {
    'pawn_1':   '♙ ',    'pawn_2':   '♟︎ ',
    'rook_1':   '♖ ',    'rook_2':   '♜ ',
    'knight_1': '♘ ',    'knight_2': '♞ ',
    'bishop_1': '♗ ',    'bishop_2': '♝ ',
    'king_1':   '♕ ',    'king_2':   '♛ ',
    'queen_1':  '♔ ',    'queen_2':  '♚ ',
    '0_0':      '__'
}


def xod(xod_data):
    eaten=[]
    cur_x = xod_data[0]
    cur_y=xod_data[1]
    new_x=xod_data[2]
    new_y=xod_data[3]
    logic=xod_data[4]
    player = xod_data[5]
    new_pos = tuple([new_x, new_y])
    if logic[cur_x][cur_y].figure == 'pawn' and player==1:
        # <=== Белая пешка
        # Возможные позиции, если пешка просто ходит
        probable_pos = []
        pos=[]

        if cur_x==6:
            probable_pos.extend(
                [tuple([cur_x-1, cur_y]),
                tuple([cur_x-2, cur_y]),
                tuple([cur_x-1, cur_y-1]),
                tuple([cur_x-1, cur_y+1])]
            )
        else:
            probable_pos.extend(
                [tuple([cur_x-1, cur_y]),
                tuple([cur_x-1, cur_y-1]),
                tuple([cur_x-1, cur_y+1])]
            )

        for x in probable_pos:
            if x[0] in range(8) and x[1] in range(8):
                pos.append(x)

        # Возможные позиции, если пешка ест

        probable_eat_pos = []
        eat_pos = []

        probable_eat_pos.extend(
            [tuple([cur_x-1, cur_y-1]),
            tuple([cur_x-1, cur_y+1])]
        )

        for x in probable_eat_pos:
            if x[0] in range(8) and x[1] in range(8):
                eat_pos.append(x)
    
        if new_pos in eat_pos:
            if logic[new_x][new_y].figure_color==2:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = Cell('pawn', 1, new_x, new_y)
                logic[cur_x][cur_y] = Cell(0, 0, cur_x, cur_y)

                return 2, logic, [eaten] # <=== - успешно, пешка съела
            else:
                return 0, 0, []
        elif new_pos in pos:
            if logic[new_x][new_y].figure==0:
                logic[new_x][new_y] = Cell('pawn', 1, new_x, new_y)
                logic[cur_x][cur_y] = Cell(0, 0, cur_x, cur_y)

                return 1,logic,[] # <=== 1 - успешно, пешка походила
            else:
                return 0,0,[] # <=== 0 - не успешно - где-то игрок ошибся!
        else:
            return 0,0,[]
        
    if logic[cur_x][cur_y].figure == 'pawn' and player==2:
        # <=== Чёрная пешка
        new_pos = tuple([new_x, new_y])

    # Возможные позиции, если пешка просто ходит

        probable_pos = []
        pos = []

        if cur_x==1:
            probable_pos.extend(
                [tuple([cur_x+1, cur_y]),
                tuple([cur_x+2, cur_y]),
                tuple([cur_x+1, cur_y-1]),
                tuple([cur_x+1, cur_y+1])]
            )
        else:
            probable_pos.extend([
                tuple([cur_x+1, cur_y]),
                tuple([cur_x+1, cur_y-1]),
                tuple([cur_x+1, cur_y+1])]
            )

        for x in probable_pos:
            if x[0] in range(8) and x[1] in range(8):
                pos.append(x)

        # Возможные позиции, если пешка ест

        probable_eat_pos = []
        eat_pos = []

        probable_eat_pos.extend(
            [tuple([cur_x+1, cur_y-1]),
            tuple([cur_x+1, cur_y+1])]
        )

        for x in probable_eat_pos:
            if x[0] in range(8) and x[1] in range(8):
                eat_pos.append(x)

    
        if new_pos in eat_pos:
            if logic[new_x][new_y].figure_color==1:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = Cell('pawn', 2, new_x, new_y)
                logic[cur_x][cur_y] = Cell(0, 0, cur_x, cur_y)

                return 2, logic, [eaten] # <=== - успешно, пешка съела
            else:
                return 0, 0, []
        elif new_pos in pos:
            if logic[new_x][new_y].figure==0:
                logic[new_x][new_y] = Cell('pawn', 2, new_x, new_y)
                logic[cur_x][cur_y] = Cell(0, 0, cur_x, cur_y)

                return 1,logic,[] # <=== 1 - успешно, пешка походила
            else:
                return 0,0,[] # <=== 0 - не успешно - где-то игрок ошибся!
        else:
            return 0,0,[]
    elif logic[cur_x][cur_y].figure =='rook':
        # Слон
        probable_pos_N = []
        probable_pos_W = []
        probable_pos_S = []
        probable_pos_E = []
        pos_N=[]
        pos_W=[]
        pos_S=[]
        pos_E=[]
        pos=[]

        probable_pos_N.extend([tuple([cur_x-i, cur_y]) for i in range(1,8)])
        probable_pos_W.extend([tuple([cur_x, cur_y-i]) for i in range(1,8)])
        probable_pos_S.extend([tuple([cur_x+i, cur_y]) for i in range(1,8)])
        probable_pos_E.extend([tuple([cur_x, cur_y+i]) for i in range(1,8)])



        for x in probable_pos_N:
            if x[0] in range(8) and x[1] in range(8):
                pos_N.append(x)
        for x in probable_pos_W:
            if x[0] in range(8) and x[1] in range(8):
                pos_W.append(x)
        for x in probable_pos_S:
            if x[0] in range(8) and x[1] in range(8):
                pos_S.append(x)
        for x in probable_pos_E:
            if x[0] in range(8) and x[1] in range(8):
                pos_E.append(x)

        if len(pos_N)!=0:
            k=0
            for x in range(0,len(pos_N)):
                if k==1:
                    break
                elif logic[pos_N[x][0]][pos_N[x][1]].figure==0:
                    pos.append(pos_N[x])
                elif logic[pos_N[x][0]][pos_N[x][1]].figure!=player:
                    pos.append(pos_N[x])
                    k=1
                elif logic[pos_N[x][0]][pos_N[x][1]].figure==player:
                    k=1

        if len(pos_W)!=0:
            k=0
            for x in range(0,len(pos_W)):
                if logic[pos_W[x][0]][pos_W[x][1]].figure==0:
                    pos.append(pos_W[x])
                elif logic[pos_W[x][0]][pos_W[x][1]].figure!=player:
                    pos.append(pos_W[x])
                    k=1
                elif logic[pos_W[x][0]][pos_W[x][1]].figure==player:
                    k=1
                if k==1:
                    break

        if len(pos_S)!=0:
            k=0
            for x in range(0,len(pos_S)):
                if logic[pos_S[x][0]][pos_S[x][1]].figure==0:
                    pos.append(pos_S[x])
                elif logic[pos_S[x][0]][pos_S[x][1]].figure!=player:
                    pos.append(pos_S[x])
                    k=1
                elif logic[pos_S[x][0]][pos_S[x][1]].figure==player:
                    k=1
                if k==1:
                    break

        if len(pos_E)!=0:
            k=0
            for x in range(0,len(pos_E)):
                if logic[pos_E[x][0]][pos_E[x][1]].figure==0:
                    pos.append(pos_E[x])
                elif logic[pos_E[x][0]][pos_E[x][1]].figure!=player:
                    pos.append(pos_E[x])
                    k=1
                elif logic[pos_E[x][0]][pos_E[x][1]].figure==player:
                    k=1
                if k==1:
                    break

        if new_pos in pos:
            if logic[new_x][new_y].figure_color!=player and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = Cell('rook', player, new_x, new_y)
                logic[cur_x][cur_y] = Cell(0, 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure==0:
                    logic[new_x][new_y] = Cell('rook', player, new_x, new_y)
                    logic[cur_x][cur_y] = Cell(0, 0, cur_x, cur_y)

                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]
    else:
        return 'wtf',logic,[]