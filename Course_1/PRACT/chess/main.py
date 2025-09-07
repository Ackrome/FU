from figures_funcs import *



### Нужные переменные

figures= {
    'pawn_1':'♙',   'pawn_2':'♟︎',
    'rook_1':'♖',   'rook_2':'♜',
    'knight_1':'♘',   'knight_2':'♞',
    'bishop_1':'♗',   'bishop_2':'♝',
    'king_1':'♔',   'king_2':'♚',
    'queen_1':'♕',   'queen_2':'♛',
    '0_0':'0'
}

colours = {
    'w' : 1,
    'b' : 2
}


positions = tuple([
    tuple(['rook_2', 'knight_2', 'bishop_2', 'king_2', 'queen_2', 'bishop_2', 'knight_2', 'rook_2']),
    tuple(['pawn_2' for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple(['pawn_1' for i in range(8)]),
    tuple(['rook_1', 'knight_1', 'bishop_1', 'king_1', 'queen_1', 'bishop_1', 'knight_1', 'rook_1'])
])




###########################################################################
### Класс игрового поля
###########################################################################

class Field():
    def __init__(self):
        self.first_gen()
        self.eaten_w = []
        self.eaten_b = []

    def first_gen(self):
        self.log= [[0 for i in range(8)] for j in range(8)]

        for i in range(8):
            for j in range(8):
                self.log[i][j]=Cell(positions[i][j][:-2] if positions[i][j] else 0, colours[positions[i][j][-1]] if positions[i][j] else 0,i,j)

    def render(self):
        pass


###########################################################################
### Класс игровой клетки поля
###########################################################################

class Cell():
    def __init__(self,figure, figure_colour,X,Y):
        self.figure = figure
        self.figure_colour = figure_colour # 0 - no, 1 - wht,2 - bls
        self.X = X
        self.Y = Y

    def __str__(self):
        return figures[str(self.figure)+'_'+str(self.figure_colour)]
game = Field()

for x in game.log:

    print(x)