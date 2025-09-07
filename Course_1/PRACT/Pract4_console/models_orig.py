import collections
###################################################################################################
### Класс клетки поля
###################################################################################################
class Cell():
    def __init__(self, figure,figure_color, X, Y):
        """
        Initialization of Cell class object
        
        Parameters
        ----------
        figure : str
            The name of the figure
        figure_color : int
            The color of the figure (0 - none, 1 - white, 2 - black)
        X : int
            The X coordinate of the cell
        Y : int
            The Y coordinate of the cell
        """
        self.figure = figure
        self.figure_color = figure_color # 0 - нет фигуры; 1 - белая фигура; 2 - чёрная фигура
        self.X = X
        self.Y = Y
###################################################################################################
### Классы фигур
###################################################################################################
class zero(Cell):
    def __str__(self):
        """
        Converts the object to string, using the coder dictionary to return the respective
        unicode symbol for the figure.
        
        Returns
        -------
        str
            The unicode symbol for the figure.
        """
        if self.figure == '0':
            return str(coder[self.figure+'_'+str(self.figure_color)])
        return str(coder[str(self.figure)+'_'+str(self.figure_color)])
    def move(self,xod_data):
        """
        Attempts to move a zero piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple indicating the result of the move.
            Format: (int, logic, list)
            Always returns (0, 0, []), as a zero piece cannot move.
        """

        return 0,0,[]
    def predict(self, xod_data,eat=0):
        """
        Predicts the possible moves of a zero piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, logic, player]
        eat : int, default=0
            Whether to predict moves that involve eating a piece.

        Returns
        -------
        list
            A list of tuples, each representing a possible move.
            Format: [(x, y), (x, y), ...]
        """
        return []
###################################################################################################
class pawn(Cell):
    def __str__(self):
        """
        Converts the pawn object to a string representation using the coder dictionary 
        to return the respective unicode symbol for the figure.

        Returns
        -------
        str
            The unicode symbol for the figure.
        """
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        """
        Makes a move for a pawn piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple indicating the result of the move.
            Format: (int, logic, list)
            Possible return values:
                0 - unsuccessful move
                1 - successful move without eating
                2 - successful move with eating
        """
        eaten=[]
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        new_x=xod_data[2]
        new_y=xod_data[3]
        logic=xod_data[4]
        player = xod_data[5]
        new_pos = tuple([new_x, new_y])
        
        if player==1:
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
                    logic[new_x][new_y] = pawn('pawn', 1, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    return 2, logic, [eaten] # <=== - успешно, пешка съела
                else:
                    return 0, 0, []
                
            elif new_pos in pos:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] =  pawn('pawn', 1, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    return 1,logic,[] # <=== 1 - успешно, пешка походила
                else:
                    return 0,0,[] # <=== 0 - не успешно - где-то игрок ошибся!
            else:
                return 0,0,[]  
                 
        if player==2:
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
                    logic[new_x][new_y] = pawn('pawn', 2, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    return 2, logic, [eaten] # <=== - успешно, пешка съела
                else:
                    return 0, 0, []
            elif new_pos in pos:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = pawn('pawn', 2, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    return 1,logic,[] # <=== 1 - успешно, пешка походила
                else:
                    return 0,0,[] # <=== 0 - не успешно - где-то игрок ошибся!
            else:
                return 0,0,[]
            
    def predict(self,xod_data,eat=0):
        """
        Predicts the possible moves of a pawn piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, logic, player]
        eat : int, default=0
            Whether to predict moves that involve eating a piece.

        Returns
        -------
        list
            A list of tuples, each representing a possible move.
            Format: [(x, y), (x, y), ...]
        """
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        
        if player==1:
            # <=== Белая пешка
            probable_pos = []
            if cur_x==6 and eat == 0:
                if cur_x-1 in range(8) and cur_y in range(8):
                    if logic[cur_x-1][cur_y].figure_color==0:
                        probable_pos.append(tuple([cur_x-1, cur_y]))
                if cur_x-2 in range(8) and cur_y in range(8):
                    if logic[cur_x-2][cur_y].figure_color==0:
                        probable_pos.append(tuple([cur_x-2, cur_y]))
            elif cur_x!=6 and eat == 0:
                if cur_x-1 in range(8) and cur_y in range(8):
                    if logic[cur_x-1][cur_y].figure_color==0:
                        probable_pos.append(tuple([cur_x-1, cur_y]))
            elif eat ==1:
                if cur_x-1 in range(8) and cur_y-1 in range(8):
                    if logic[cur_x-1][cur_y-1].figure!=player and logic[cur_x-1][cur_y-1].figure!=0 :
                        probable_pos.append(tuple([cur_x-1, cur_y-1]))
                if cur_x-1 in range(8) and cur_y+1 in range(8):
                    if logic[cur_x-1][cur_y+1].figure!=player and logic[cur_x-1][cur_y+1].figure!=0:
                        probable_pos.append(tuple([cur_x-1, cur_y+1]))
            return probable_pos   
         
        if player==2:
            
            # <=== Чёрная пешка
            probable_pos = []

            if cur_x==1 and eat == 0:
                if cur_x+1 in range(8) and cur_y in range(8):
                    if logic[cur_x+1][cur_y].figure_color==0:
                        probable_pos.append(tuple([cur_x+1, cur_y]))
                if cur_x+2 in range(8) and cur_y in range(8):
                    if logic[cur_x+2][cur_y].figure_color==0:
                        probable_pos.append(tuple([cur_x+2, cur_y]))
            elif cur_x!=1 and eat == 0:
                if cur_x+1 in range(8) and cur_y in range(8):
                    if logic[cur_x+1][cur_y].figure_color==0:
                        probable_pos.append(tuple([cur_x+1, cur_y]))
            elif eat ==1:
                if cur_x+1 in range(8) and cur_y-1 in range(8):
                    if logic[cur_x+1][cur_y-1].figure!=2 and logic[cur_x+1][cur_y-1].figure!=0:
                        probable_pos.append(tuple([cur_x+1, cur_y-1]))
                if cur_x+1 in range(8) and cur_y+1 in range(8):
                    if logic[cur_x+1][cur_y+1].figure!=2 and logic[cur_x+1][cur_y+1].figure!=0:
                        probable_pos.append(tuple([cur_x+1, cur_y+1]))
            return probable_pos
        return []
###################################################################################################
class rook(Cell):
    def __str__(self):
        """
        Converts the object to string, using the coder dictionary to return the respective
        unicode symbol for the figure.
        
        Returns
        -------
        str
            The unicode symbol for the figure.
        """
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        """
        Executes a move for the rook on the board based on the given move data.

        Parameters
        ----------
        xod_data : list
            A list containing the current position, new position, the game logic, and the player.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple containing the status of the move, the updated game logic, and any eaten piece.
            Status: 2 if a piece was eaten, 1 if the move was successful, 0 if the move was not successful.
        """
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
                    
            
            if logic[new_x][new_y].figure_color!=player and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = rook('rook', player, new_x, new_y)
                logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = rook('rook', player, new_x, new_y)
                    logic[cur_x][cur_y] = zero('0', 0, cur_x, cur_y)

                    
                    
                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]
        
    def predict(self,xod_data,eat=0):
        """
        Predicts all possible moves for a rook piece from (cur_x, cur_y) on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, logic, player]
        eat : int, optional
            Whether to look for eat moves or not.

        Returns
        -------
        list of tuples
            A list of possible moves for the piece.
        """
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        probable_pos_N = []
        probable_pos_W = []
        probable_pos_S = []
        probable_pos_E = []
        pos_N=[]
        pos_W=[]
        pos_S=[]
        pos_E=[]
        pos=[]
        eat_pos=[]

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
                elif logic[pos_N[x][0]][pos_N[x][1]].figure_color==0:
                    pos.append(pos_N[x])
                elif logic[pos_N[x][0]][pos_N[x][1]].figure_color!=player:
                    eat_pos.append(pos_N[x])
                    k=1
                elif logic[pos_N[x][0]][pos_N[x][1]].figure_color==player:
                    k=1
                    break

        if len(pos_W)!=0:
            k=0
            for x in range(0,len(pos_W)):
                if k==1:
                    break
                elif logic[pos_W[x][0]][pos_W[x][1]].figure_color==player:
                    k=1
                    break
                elif logic[pos_W[x][0]][pos_W[x][1]].figure_color==0:
                    pos.append(pos_W[x])
                elif logic[pos_W[x][0]][pos_W[x][1]].figure_color==(3-player) and logic[pos_W[x][0]][pos_W[x][1]].figure_color!=0:
                    eat_pos.append(pos_W[x])
                    k=1

        if len(pos_S)!=0:
            k=0
            for x in range(0,len(pos_S)):
                if k==1:
                    break
                elif logic[pos_S[x][0]][pos_S[x][1]].figure_color==0:
                    pos.append(pos_S[x])
                elif logic[pos_S[x][0]][pos_S[x][1]].figure_color==(3-player) and logic[pos_S[x][0]][pos_S[x][1]].figure!=0:
                    eat_pos.append(pos_S[x])
                    k=1
                elif logic[pos_S[x][0]][pos_S[x][1]].figure_color==player:
                    k=1
                    break
        if len(pos_E)!=0:
            k=0
            for x in range(0,len(pos_E)):
                if logic[pos_E[x][0]][pos_E[x][1]].figure_color==0:
                    pos.append(pos_E[x])
                elif logic[pos_E[x][0]][pos_E[x][1]].figure_color==(3-player) and logic[pos_E[x][0]][pos_E[x][1]].figure!=0:
                    eat_pos.append(pos_E[x])
                    k=1
                elif logic[pos_E[x][0]][pos_E[x][1]].figure_color==player:
                    k=1
                    break
        if eat==1:
            return eat_pos
        return pos 
###################################################################################################
class knight(Cell):
    def __str__(self):
        """
        Converts the knight object to a string representation using the coder dictionary.

        Returns
        -------
        str
            The unicode symbol representing the knight figure based on its color.
        """
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        
        """
        Attempts to move a knight piece from (cur_x, cur_y) to (new_x, new_y) on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple indicating the result of the move.
            Format: (int, logic, list)
        """
        eaten=[]
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        new_x=xod_data[2]
        new_y=xod_data[3]
        logic=xod_data[4]
        player = xod_data[5]
        new_pos = tuple([new_x, new_y])
        probable_pos=[]
        pos=[]
        probable_pos.extend([ tuple([cur_x+x,cur_y+y]) for x in range(-2,3) for y in range(-2,3) if not(x==0 or y==0 or (abs(x)+abs(y))!=3)])
        for x in probable_pos:
            if x[0] in range(8) and x[1] in range(8):
                pos.append(x)
        
        if new_pos in pos:
            if logic[new_x][new_y].figure_color!=player and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = knight('knight', player, new_x, new_y)
                logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = knight('knight', player, new_x, new_y)
                    logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)
                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]
        
    def predict(self,xod_data,eat=0):
        
        """
        Predicts the possible moves of a knight piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, logic, player]
        eat : int, default=0
            Whether to predict moves that involve eating a piece.

        Returns
        -------
        list
            A list of tuples, each representing a possible move.
            Format: [(x, y), (x, y), ...]
        """
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        probable_pos=[]
        pos=[]
        poses=[]
        eat_pos=[]
        probable_pos.extend([ tuple([cur_x+x,cur_y+y]) for x in range(-2,3) for y in range(-2,3) if not(x==0 or y==0 or (abs(x)+abs(y))!=3)])
        for x in probable_pos:
            if x[0] in range(8) and x[1] in range(8):
                pos.append(x)
        for x in pos:
            if logic[x[0]][x[1]].figure_color==0:
                poses.append(x)
            elif logic[x[0]][x[1]].figure_color==3-player:
                eat_pos.append(x)
        if eat==1:
            return eat_pos
        return poses
###################################################################################################
class bishop(Cell):
    def __str__(self):
        """
        Converts the bishop object to a string representation using the coder dictionary 
        to return the respective unicode symbol for the figure.

        Returns
        -------
        str
            The unicode symbol for the bishop figure based on its color.
        """

        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        """
        Makes a move for a bishop piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple indicating the result of the move.
            Format: (int, logic, list)
            Possible return values:
                0 - unsuccessful move
                1 - successful move without eating
                2 - successful move with eating
        """
        eaten=[]
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        new_x=xod_data[2]
        new_y=xod_data[3]
        logic=xod_data[4]
        player = xod_data[5]
        new_pos = tuple([new_x, new_y])
        
        probable_pos_NW = []
        probable_pos_SW = []
        probable_pos_SE = []
        probable_pos_NE = []
        pos_NW=[]
        pos_SW=[]
        pos_SE=[]
        pos_NE=[]
        pos=[]

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
                    pos.append(pos_NW[x])
                    k=1
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
                    pos.append(pos_SW[x])
                    k=1
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
                    pos.append(pos_SE[x])
                    k=1
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
                    pos.append(pos_NE[x])
                    k=1
                elif logic[pos_NE[x][0]][pos_NE[x][1]].figure_color==player:
                    k=1
        if new_pos in pos:
            if logic[new_x][new_y].figure_color!=player and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = bishop('bishop', player, new_x, new_y)
                logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = bishop('bishop', player, new_x, new_y)
                    logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]
    def predict(self,xod_data,eat=0):
        """
        Predicts possible moves for a piece on the board.

        Parameters
        ----------
        xod_data : list
            Contains the current position and state of the game.
            Format: [cur_x, cur_y, logic, player]
        eat : int, optional
            Indicates whether to look for capturing moves (default is 0).

        Returns
        -------
        list
            A list of tuples representing possible moves or capturing moves,
            depending on the 'eat' parameter.
        """
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
                    k=1
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
                    k=1
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
                    k=1
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
                    k=1
                elif logic[pos_NE[x][0]][pos_NE[x][1]].figure_color==player:
                    k=1
        if eat==1:
            return eat_pos
        return pos
###################################################################################################
class king(Cell):
    def __str__(self):
        """
        Converts the king object to a string representation using the coder dictionary 
        to return the respective unicode symbol for the figure.

        Returns
        -------
        str
            The unicode symbol for the king figure based on its color.
        """
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
        """
        Moves the king to a new position on the board.

        Parameters
        ----------
        xod_data : list
            Contains the current position and state of the game.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple containing the move type (1 or 2), the new state of the board, and a list of eaten figures.
        """
        eaten=[]
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        new_x=xod_data[2]
        new_y=xod_data[3]
        logic=xod_data[4]
        player = xod_data[5]
        new_pos = tuple([new_x, new_y])
        probable_pos=[]
        probable_pos.extend([
            tuple([cur_x+1,cur_y]),
            tuple([cur_x+1,cur_y+1]),
            tuple([cur_x,cur_y+1]),
            tuple([cur_x-1,cur_y+1]),
            tuple([cur_x-1,cur_y]),
            tuple([cur_x-1,cur_y-1]),
            tuple([cur_x+1,cur_y-1]),
            tuple([cur_x,cur_y-1])
        ])

        pos =[i for i in probable_pos if i[0] in range(8) and i[1] in range(8)]      
        if new_pos in pos:
            if logic[new_x][new_y].figure_color!=player and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = king('king', player, new_x, new_y)
                logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = king('king', player, new_x, new_y)
                    logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)
                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]
    def predict(self,xod_data,eat=0):
        """
        Predicts the possible moves of a king piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, logic, player]
        eat : int, default=0
            Whether to predict moves that involve eating a piece.

        Returns
        -------
        list
            A list of tuples, each representing a possible move.
            Format: [(x, y), (x, y), ...]
        """
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        probable_pos=[]
        pos=[]
        poses=[]
        eat_pos=[]

        probable_pos.extend([
            tuple([cur_x+1,cur_y]),
            tuple([cur_x+1,cur_y+1]),
            tuple([cur_x,cur_y+1]),
            tuple([cur_x-1,cur_y+1]),
            tuple([cur_x-1,cur_y]),
            tuple([cur_x-1,cur_y-1]),
            tuple([cur_x+1,cur_y-1]),
            tuple([cur_x,cur_y-1])
        ])

        for x in probable_pos:
            if x[0] in range(8) and x[1] in range(8):
                pos.append(x)
        
        for x in pos:
            if logic[x[0]][x[1]].figure_color==0:
                poses.append(x)
            elif logic[x[0]][x[1]].figure_color==3-player:
                eat_pos.append(x)
        if eat==1:
            return eat_pos
        return poses   
###################################################################################################
class queen(Cell):
    def __str__(self):
        """
        Converts the queen object to a string representation using the coder dictionary 
        to return the respective unicode symbol for the figure.

        Returns
        -------
        str
            The unicode symbol for the figure.
        """
        return str(coder[self.figure+'_'+str(self.figure_color)])  
    def move(self,xod_data):
            
        """
        Moves a queen piece on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, new_x, new_y, logic, player]

        Returns
        -------
        tuple
            A tuple with the result of the move, the new game state, and the figure that was eaten.
            Format: (int, list, list)
        """
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
            if logic[new_x][new_y].figure_color!=player and logic[new_x][new_y].figure_color!=0:
                eaten = logic[new_x][new_y].figure + '_' + str(logic[new_x][new_y].figure_color)
                logic[new_x][new_y] = queen('queen', player, new_x, new_y)
                logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                return 2, logic, [eaten]
            
            elif logic[new_x][new_y].figure_color==0:
                if logic[new_x][new_y].figure_color==0:
                    logic[new_x][new_y] = queen('queen', player, new_x, new_y)
                    logic[cur_x][cur_y] = zero(0, 0, cur_x, cur_y)

                    return 1,logic,[]
                else:
                    return 0,0,[]
            else:
                return 0,0,[]
        else:
            return 0,0,[]    
    def predict(self,xod_data,eat=0):  
        """
        Predicts all possible moves for a queen piece from (cur_x, cur_y) on the board.

        Parameters
        ----------
        xod_data : list
            List containing move data and current game state.
            Format: [cur_x, cur_y, logic, player]
        eat : int, optional
            Whether to look for eat moves or not.

        Returns
        -------
        list of tuples
            A list of possible moves for the piece.
        """
        cur_x = xod_data[0]
        cur_y=xod_data[1]
        logic=xod_data[2]
        player = xod_data[3]
        
        probable_pos_N = []
        probable_pos_W = []
        probable_pos_S = []
        probable_pos_E = []
        pos_N=[]
        pos_W=[]
        pos_S=[]
        pos_E=[]
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


        probable_pos_N.extend([tuple([cur_x-i, cur_y]) for i in range(1,8)])
        probable_pos_W.extend([tuple([cur_x, cur_y-i]) for i in range(1,8)])
        probable_pos_S.extend([tuple([cur_x+i, cur_y]) for i in range(1,8)])
        probable_pos_E.extend([tuple([cur_x, cur_y+i]) for i in range(1,8)])
        probable_pos_NW.extend([tuple([cur_x-i, cur_y-i]) for i in range(1,8)])
        probable_pos_SW.extend([tuple([cur_x+i, cur_y-i]) for i in range(1,8)])
        probable_pos_SE.extend([tuple([cur_x+i, cur_y+i]) for i in range(1,8)])
        probable_pos_NE.extend([tuple([cur_x-i, cur_y+i]) for i in range(1,8)])


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


        if len(pos_N)!=0:
            k=0
            for x in range(0,len(pos_N)):
                if k==1:
                    break
                elif logic[pos_N[x][0]][pos_N[x][1]].figure_color==0:
                    pos.append(pos_N[x])
                elif logic[pos_N[x][0]][pos_N[x][1]].figure_color!=player:
                    eat_pos.append(pos_N[x])
                    k=1
                elif logic[pos_N[x][0]][pos_N[x][1]].figure_color==player:
                    k=1

        if len(pos_W)!=0:
            k=0
            for x in range(0,len(pos_W)):
                if logic[pos_W[x][0]][pos_W[x][1]].figure_color==0:
                    pos.append(pos_W[x])
                elif logic[pos_W[x][0]][pos_W[x][1]].figure_color!=player:
                    eat_pos.append(pos_W[x])
                    k=1
                elif logic[pos_W[x][0]][pos_W[x][1]].figure_color==player:
                    k=1
                if k==1:
                    break

        if len(pos_S)!=0:
            k=0
            for x in range(0,len(pos_S)):
                if logic[pos_S[x][0]][pos_S[x][1]].figure_color==0:
                    pos.append(pos_S[x])
                elif logic[pos_S[x][0]][pos_S[x][1]].figure_color!=player:
                    eat_pos.append(pos_S[x])
                    k=1
                elif logic[pos_S[x][0]][pos_S[x][1]].figure_color==player:
                    k=1
                if k==1:
                    break

        if len(pos_E)!=0:
            k=0
            for x in range(0,len(pos_E)):
                if logic[pos_E[x][0]][pos_E[x][1]].figure_color==0:
                    pos.append(pos_E[x])
                elif logic[pos_E[x][0]][pos_E[x][1]].figure_color!=player:
                    eat_pos.append(pos_E[x])
                    k=1
                elif logic[pos_E[x][0]][pos_E[x][1]].figure_color==player:
                    k=1
                if k==1:
                    break

        if len(pos_NW)!=0:
            k=0
            for x in range(0,len(pos_NW)):
                if logic[pos_NW[x][0]][pos_NW[x][1]].figure_color==0:
                    pos.append(pos_NW[x])
                elif logic[pos_NW[x][0]][pos_NW[x][1]].figure_color!=player:
                    eat_pos.append(pos_NW[x])
                    k=1
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
                    k=1
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
                    k=1
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
                    k=1
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
    'pawn': pawn,
    'rook': rook,
    'knight': knight,
    'bishop': bishop,
    'king': king,
    'queen': queen,
    '0': zero,
    0: zero
}
coder = {
    'pawn_1':   '♙ ',    'pawn_2':   '♟︎ ',
    'rook_1':   '♖ ',    'rook_2':   '♜ ',
    'knight_1': '♘ ',    'knight_2': '♞ ',
    'bishop_1': '♗ ',    'bishop_2': '♝ ',
    'king_1':   '♔ ',    'king_2':   '♚ ',
    'queen_1':  '♕ ',    'queen_2':  '♛ ',
    '0_0':      '  '
}
start_positions = tuple([
    tuple(['rook_2', 'knight_2', 'bishop_2',  'queen_2','king_2', 'bishop_2', 'knight_2', 'rook_2']),
    tuple(['pawn_2' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['pawn_1' for i in range(8)]),
    tuple(['rook_1', 'knight_1', 'bishop_1',  'queen_1', 'king_1', 'bishop_1', 'knight_1', 'rook_1']),
])
###################################################################################################
### Класс поля
###################################################################################################
class Field():
    def __init__(self, logic=None):
        """
        Initialize a new game field instance.

        Parameters
        ----------
        logic : list of lists, optional
            A two-dimensional list representing the game board. The default is None.

        Attributes
        ----------
        logic : list of lists
            A two-dimensional list representing the game board.
        """
        self.logic = logic if logic else self.first_generation()

    def first_generation(self):
        """
        Method for generating the initial state of the board.

        Generates a two-dimensional list representing the game board, based on the start_positions tuple.

        Returns
        -------
        logic : list of lists
            A two-dimensional list representing the initial state of the game board.
        """
        logic = [[0 for i in range(8)] for j in range(8)] # <=== Логическое представление игрового поля, его модель

        for i in range(8):
            for j in range(8):
                logic[i][j] = figure_classes[start_positions[i][j][:-2]](figure=start_positions[i][j][:-2],figure_color=int(start_positions[i][j][-1]), X=i, Y=j)

        return logic
    
    def predict_danger(self, logic, play, l=0):
        """
        Predicts the positions that can be attacked by the opponent in the given turn.

        Parameters
        ----------
        logic : list of lists
            A two-dimensional list representing the game board.
        play : int
            The index of the player currently making the move (0 or 1).
        l : int
            The number of the move being made.

        Returns
        -------
        list
            A list of coordinates that can be attacked by the opponent in the given turn.
        """
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
        """
        Renders the current state of the game board.

        Parameters
        ----------
        moves : int
            The number of the current move.
        eaten : list of str
            A list of eaten figures in the format 'figure_color', where 'color' is '1' for white and '2' for black.
        predictlist : list of tuples, optional
            A list of coordinates of possible moves without eating.
        eat_predictlist : list of tuples, optional
            A list of coordinates of possible moves with eating.
        danger_predictlist : list of tuples, optional
            A list of coordinates of figures that can be attacked.
        chekking_list : list of tuples, optional
            A list of coordinates of figures that can attack the king.
        linking_dict : dict, optional
            A dictionary of coordinates of figures that can attack the king.

        Returns
        -------
        None
        """
        
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
