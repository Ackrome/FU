


### !!!ВАЖНО: методы хода фигур возвращают кортеж вида (a, b, c), где:
### a - результат хода: a=0 - неудачный ход, a=1 - фигура походила, a=2 - фигура съела
### b - новый logic
### с - съеденная фигура, если такая есть (в противном случае = 0)


###################################################################################################
### Классы фигур
###################################################################################################
    
class figure():

    def __init__(self, color, x, y):

        self.color = color
        self.x = x
        self.y = y


###################################################################################################

class pawn(figure):
    def probable_poses_check(self, logic: list) -> tuple:
        cur_x = self.x
        cur_y = self.y

        probable_probable_poses = []
        probable_poses = []

        probable_probable_eat_poses = []
        probable_eat_poses = []

        result = []

        if self.color == 1:

            if cur_x==6:
                probable_probable_poses.extend([
                    (cur_x-1, cur_y),
                    (cur_x-2, cur_y),
                ])
            else:
                probable_probable_poses.append((cur_x-1, cur_y))

            for x in probable_probable_poses:
                if x[0] in range(8) and x[1] in range(8):
                    probable_poses.append(x)

            probable_probable_eat_poses.extend([
                (cur_x-1, cur_y-1),
                (cur_x-1, cur_y+1),
            ])

            for x in probable_probable_eat_poses:
                if x[0] in range(8) and x[1] in range(8):
                    probable_eat_poses.append(x)

        else:

            if cur_x==1:
                probable_probable_poses.extend([
                    (cur_x+1, cur_y),
                    (cur_x+2, cur_y),
                ])
            else:
                probable_probable_poses.append((cur_x+1, cur_y))

            for x in probable_probable_poses:
                if x[0] in range(8) and x[1] in range(8):
                    probable_poses.append(x)

            probable_probable_eat_poses.extend([
                (cur_x+1, cur_y-1),
                (cur_x+1, cur_y+1),
            ])

            for x in probable_probable_eat_poses:
                if x[0] in range(8) and x[1] in range(8):
                    probable_eat_poses.append(x)

        for new_x, new_y in probable_poses:

            if logic[new_x][new_y] == 0:
                result.append((new_x, new_y))
        
        for new_x, new_y in probable_eat_poses:

            if logic[new_x][new_y] and logic[new_x][new_y].color != self.color:
                result.append((new_x, new_y))

        return tuple(result)


    def move(self, logic: list, new_x: int, new_y: int, probable_poses: tuple) -> tuple:
        logic = [x[::] for x in logic][::]
        cur_x = self.x
        cur_y = self.y
        new_pos = (new_x, new_y)

        # Создание нового logic и возвращение результата хода

        if new_pos in probable_poses:
            if logic[new_x][new_y] == 0:
                logic[new_x][new_y] = pawn(self.color, new_x, new_y)
                logic[cur_x][cur_y] = 0

                return (1, logic, 0) # 1 => moved successfully
            
            if logic[new_x][new_y].color != self.color:
                eaten = logic[new_x][new_y]
                logic[new_x][new_y] = pawn(self.color, new_x, new_y)
                logic[cur_x][cur_y] = 0

                return (2, logic, eaten) # 2 => eaten successfully
        
        return (0, 0, 0) # 0 => Player entered wrong positions
    

    def __str__(self):
        return 'P' if self.color==1 else 'p'
    

    def name(self):
        return 'Pawn'
    

###################################################################################################

class rook(figure):
    def probable_poses_check(self, logic: list):
        cur_x = self.x
        cur_y = self.y

        probable_poses = []

        # vertical
        for probable_x in range(cur_x+1, 8):
            if logic[probable_x][cur_y]==0:
                probable_poses.append((probable_x, cur_y))

            elif logic[probable_x][cur_y].color!=self.color:
                probable_poses.append((probable_x, cur_y))
                break
            else:
                break
        
        for probable_x in range(cur_x-1, -1, -1):
            if logic[probable_x][cur_y]==0:
                probable_poses.append((probable_x, cur_y))

            elif logic[probable_x][cur_y].color!=self.color:
                probable_poses.append((probable_x, cur_y))
                break
            else:
                break

        # horizontal
        for probable_y in range(cur_y+1, 8):
            if logic[cur_x][probable_y]==0:
                probable_poses.append((cur_x, probable_y))
                
            elif logic[cur_x][probable_y].color!=self.color:
                probable_poses.append((cur_x, probable_y))
                break
            else:
                break
        
        for probable_y in range(cur_y-1, -1, -1):
            if logic[cur_x][probable_y]==0:
                probable_poses.append((cur_x, probable_y))

            elif logic[cur_x][probable_y].color!=self.color:
                probable_poses.append((cur_x, probable_y))
                break
            else:
                break

        return tuple(probable_poses)


    def move(self, logic: list, new_x: int, new_y: int, probable_poses: tuple) -> tuple:
        logic = [x[::] for x in logic][::]
        cur_x = self.x
        cur_y = self.y
        new_pos = tuple([new_x, new_y])

        if new_pos in probable_poses:
            if logic[new_x][new_y] == 0:
                logic[new_x][new_y] = rook(self.color, new_x, new_y)
                logic[cur_x][cur_y] = 0

                return (1, logic, 0) # 1 => moved successfully
            
            if logic[new_x][new_y].color != self.color:
                eaten = logic[new_x][new_y]
                logic[new_x][new_y] = rook(self.color, new_x, new_y)
                logic[cur_x][cur_y] = 0

                return (2, logic, eaten) # 2 => eaten successfully
        
        return (0, 0, 0) # 0 => Player entered wrong positions
    

    def __str__(self):
        return 'R' if self.color==1 else 'r'
    

    def name(self):
        return 'Rook'
    

###################################################################################################
    
class knight(figure):
    def probable_poses_check(self, logic):
        cur_x, cur_y = self.x, self.y

        probable_poses = []
        probable_probable_poses = ( # probable positions inluding out-of-field ones
            (cur_x-2, cur_y-1),
            (cur_x-2, cur_y+1),
            (cur_x-1, cur_y-2),
            (cur_x-1, cur_y+2),
            (cur_x+1, cur_y-2),
            (cur_x+1, cur_y+2),
            (cur_x+2, cur_y-1),
            (cur_x+2, cur_y+1),
        )

        for pos in probable_probable_poses: 
            if pos[0] in range(8) and pos[1] in range(8): # убирем выходящие за поле варианты
                if not logic[pos[0]][pos[1]]:  # оставляем только пустые клетки и фигуры противника
                    probable_poses.append(pos)

                elif logic[pos[0]][pos[1]].color!=self.color:
                    probable_poses.append(pos)


        return tuple(probable_poses)
    

    def move(self, logic: list, new_x: int, new_y: int, probable_poses: tuple) -> tuple:
        logic = [x[::] for x in logic][::]
        cur_x = self.x
        cur_y = self.y
        new_pos = (new_x, new_y)

        if new_pos in probable_poses:
            if logic[new_x][new_y] == 0:
                logic[new_x][new_y] = knight(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (1, logic, 0) # 1 => moved successfully
            
            elif logic[new_x][new_y].color != self.color:
                eaten = logic[new_x][new_y]
                logic[new_x][new_y] = knight(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (2, logic, eaten) # 2 => eaten successfully
            
        return (0, 0, 0) # 0 => Player entered wrong positions
    

    def __str__(self):
        return 'H' if self.color==1 else 'h'
    

    def name(self):
        return 'Horse'
    

###################################################################################################
    
class bishop(figure):
    def probable_poses_check(self, logic:list) -> tuple:
        cur_x, cur_y = self.x, self.x

        probable_poses = []

        # major diag
        for delt in range(1, min(7-cur_x, 7-cur_y)+1):
            if logic[cur_x+delt][cur_y+delt]==0:
                probable_poses.append((cur_x+delt, cur_y+delt))

            elif logic[cur_x+delt][cur_y+delt].color!=self.color:
                probable_poses.append((cur_x+delt, cur_y+delt))
                break
            else:
                break
        
        for delt in range(1, min(cur_x, cur_y)+1):
            if logic[cur_x-delt][cur_y-delt]==0:
                probable_poses.append((cur_x-delt, cur_y-delt))

            elif logic[cur_x-delt][cur_y-delt].color!=self.color:
                probable_poses.append((cur_x-delt, cur_y-delt))
                break
            else:
                break

        # minor diag
        for delt in range(1, min(cur_x, 7-cur_y)+1):
            if logic[cur_x-delt][cur_y+delt]==0:
                probable_poses.append((cur_x-delt, cur_y+delt))

            elif logic[cur_x-delt][cur_y+delt].color!=self.color:
                probable_poses.append((cur_x-delt, cur_y+delt))
                break
            else:
                break
        
        for delt in range(1, min(7-cur_x, cur_y)+1):
            if logic[cur_x+delt][cur_y-delt]==0:
                probable_poses.append((cur_x+delt, cur_y-delt))

            elif logic[cur_x+delt][cur_y-delt].color!=self.color:
                probable_poses.append((cur_x+delt, cur_y-delt))
                break
            else:
                break

        return tuple(probable_poses)
    

    def move(self, logic: list, new_x: int, new_y: int, probable_poses: tuple) -> tuple:
        logic = [x[::] for x in logic][::]
        cur_x = self.x
        cur_y = self.y
        new_pos = (new_x, new_y)

        if new_pos in probable_poses:
            if logic[new_x][new_y] == 0:
                logic[new_x][new_y] = bishop(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (1, logic, 0) # 1 => moved successfully
            
            elif logic[new_x][new_y].color != self.color:
                eaten = logic[new_x][new_y]
                logic[new_x][new_y] = bishop(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (2, logic, eaten) # 2 => eaten successfully
            
        return (0, 0, 0) # 0 => Player entered wrong positions
    

    def __str__(self):
        return 'B' if self.color==1 else 'b'
    

    def name(self):
        return 'Bishop'


###################################################################################################
    
class king(figure):
    def probable_poses_check(self, logic):
        cur_x, cur_y = self.x, self.y

        probable_poses = []
        probable_probable_poses = (
            (cur_x-1, cur_y-1),
            (cur_x-1, cur_y),
            (cur_x-1, cur_y+1),
            (cur_x, cur_y-1),
            (cur_x, cur_y+1),
            (cur_x+1, cur_y-1),
            (cur_x+1, cur_y),
            (cur_x+1, cur_y+1),
        )

        for pos in probable_probable_poses:
            if pos[0] in range(8) and pos[1] in range(8): # убирем выходящие за поле варианты
                if not logic[pos[0]][pos[1]]:  # оставляем только пустые клетки и фигуры противника
                    probable_poses.append(pos)

                elif logic[pos[0]][pos[1]].color!=self.color:
                    probable_poses.append(pos)

        return tuple(probable_poses)


    def move(self, logic: list, new_x: int, new_y: int, probable_poses: tuple) -> tuple:
        logic = [x[::] for x in logic][::]
        cur_x = self.x
        cur_y = self.y
        new_pos = (new_x, new_y)

        if new_pos in probable_poses:
            if logic[new_x][new_y] == 0:
                logic[new_x][new_y] = king(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (1, logic, 0) # 1 => moved successfully
            
            elif logic[new_x][new_y].color != self.color:
                eaten = logic[new_x][new_y]
                logic[new_x][new_y] = king(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (2, logic, eaten) # 2 => eaten successfully
            
        return (0, 0, 0) # 0 => Player entered wrong positions
    

    def __str__(self):
        return 'K' if self.color==1 else 'k'
    

    def name(self):
        return 'King'
    

###################################################################################################
    
class queen(figure):
    def probable_poses_check(self, logic: list) -> tuple:
        cur_x, cur_y = self.x, self.y

        probable_poses = []

        # vertical
        for probable_x in range(cur_x+1, 8):
            if logic[probable_x][cur_y]==0:
                probable_poses.append((probable_x, cur_y))

            elif logic[probable_x][cur_y].color!=self.color:
                probable_poses.append((probable_x, cur_y))
                break
            else:
                break
        
        for probable_x in range(cur_x-1, -1, -1):
            if logic[probable_x][cur_y]==0:
                probable_poses.append((probable_x, cur_y))

            elif logic[probable_x][cur_y].color!=self.color:
                probable_poses.append((probable_x, cur_y))
                break
            else:
                break

        # major diag
        for delt in range(1, min(7-cur_x, 7-cur_y)+1):
            if logic[cur_x+delt][cur_y+delt]==0:
                probable_poses.append((cur_x+delt, cur_y+delt))

            elif logic[cur_x+delt][cur_y+delt].color!=self.color:
                probable_poses.append((cur_x+delt, cur_y+delt))
                break
            else:
                break
        
        for delt in range(1, min(cur_x, cur_y)+1):
            if logic[cur_x-delt][cur_y-delt]==0:
                probable_poses.append((cur_x-delt, cur_y-delt))

            elif logic[cur_x-delt][cur_y-delt].color!=self.color:
                probable_poses.append((cur_x-delt, cur_y-delt))
                break
            else:
                break

        # minor diag
        for delt in range(1, min(cur_x, 7-cur_y)+1):
            if logic[cur_x-delt][cur_y+delt]==0:
                probable_poses.append((cur_x-delt, cur_y+delt))

            elif logic[cur_x-delt][cur_y+delt].color!=self.color:
                probable_poses.append((cur_x-delt, cur_y+delt))
                break
            else:
                break
        
        for delt in range(1, min(7-cur_x, cur_y)+1):
            if logic[cur_x+delt][cur_y-delt]==0:
                probable_poses.append((cur_x+delt, cur_y-delt))

            elif logic[cur_x+delt][cur_y-delt].color!=self.color:
                probable_poses.append((cur_x+delt, cur_y-delt))
                break
            else:
                break

        return tuple(probable_poses)
    

    def move(self, logic: list, new_x: int, new_y: int, probable_poses: tuple) -> tuple:
        logic = [x[::] for x in logic][::]
        cur_x = self.x
        cur_y = self.y
        new_pos = (new_x, new_y)

        if new_pos in probable_poses:
            if logic[new_x][new_y]==0:
                logic[new_x][new_y] = queen(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (1, logic, 0) # 1 => moved successfully
            
            elif logic[new_x][new_y].color != self.color:
                eaten = logic[new_x][new_y]
                logic[new_x][new_y] = queen(self.color, *new_pos)
                logic[cur_x][cur_y] = 0

                return (2, logic, eaten) # 2 => eaten successfully
            
        return (0, 0, 0) # 0 => Player entered wrong positions
    

    def __str__(self):
        return 'Q' if self.color==1 else 'q'
    

    def name(self):
        return 'Queen'


###################################################################################################
### Необходимые переменные
###################################################################################################

coder = {
    'pawn_1':   'P',    'pawn_2':   'p',
    'rook_1':   'R',    'rook_2':   'r',
    'knight_1': 'H',    'knight_2': 'h',
    'bishop_1': 'B',    'bishop_2': 'b',
    'king_1':   'K',    'king_2':   'k',
    'queen_1':  'Q',    'queen_2':  'q',
    '0_0': '.',
}

figure_classes = {
    'pawn': pawn,
    'rook': rook,
    'knight': knight,
    'bishop': bishop,
    'king': king,
    'queen': queen,
}

start_positions = tuple([
    ('rook_2', 'knight_2', 'bishop_2',  'queen_2', 'king_2','bishop_2', 'knight_2', 'rook_2'),
    tuple(['pawn_2' for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple([0 for i in range(8)]),
    tuple(['pawn_1' for i in range(8)]),
    ('rook_1', 'knight_1', 'bishop_1', 'queen_1', 'king_1', 'bishop_1', 'knight_1', 'rook_1'),
])
    
###################################################################################################
### Необходимые функции
###################################################################################################

def danger_poses_check(x, y, logic) -> tuple:
        result = []

        for row in logic:
            for cell in row:
                if cell:
                    sub_probable_poses = cell.probable_poses_check(logic)

                    if (x, y) in sub_probable_poses:
                        result.append((cell.x, cell.y))

        return tuple(result)


def possible(s: str) -> str:
    return '\033[30;30;42m'+s+'\033[0;37;40m'


def possible_to_eat(s: str) -> str:
    return '\033[0;2;43m'+s+'\033[0;37;40m'



def danger(s: str) -> str:
    return '\033[0;2;41m'+s+'\033[0;37;40m'



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
                cell = start_positions[i][j]

                if cell:
                    logic[i][j] = figure_classes[cell[:-2]](color=int(cell[-1]), x=i, y=j)

        return logic
                
                
    def render(self, c: int, p1: str, p2: str, e1: str, e2: str, possible_poses: tuple=(), danger_poses: tuple=()) -> str:
        result = []

        # Игровое поле
        field = [
            '.'*23,
            '|' + '\033[1;36;40m   A B C D E F G H   \033[0;37;40m' + '|',
            '|' + ' '*21 + '|',
        ]

        for i in range(8):
            row = f'|\033[1;36;40m{8-i}  \033[0;37;40m'

            for j in range(8):
                cll = self.logic[i][j]

                if (i, j) in possible_poses:
                    cll = possible_to_eat(str(cll).center(2)) if cll else possible('.'.center(2))

                elif (i, j) in danger_poses:
                    cll = danger(str(cll).center(2))
                
                else:
                    cll = str(cll).center(2) if cll else '.'.center(2)

                row += cll
            
            row += f'\033[1;36;40m {8-i}\033[0;37;40m|'

            field.append(row)
        
        field.extend(['|' + ' '*21 + '|',
                    '|\033[1;36;40m   A B C D E F G H   \033[0;37;40m|',
                    "'"*23])
        
        # Статистика
        stats = ['' for i in range(2)]

        stats.append(f'')
        stats.append(f'{" "*5}\033[30;2;47m{p1}\033[0;37;40m: {", ".join(e1)}')
        stats.extend([
            '',
            '',
            '',
            f'{" "*5}Было сделано ходов: {c}',
            '',
            '',
            '',
        ])
        stats.append(f'{" "*5}\033[0;2;40m{p2}\033[0;37;40m: {", ".join(e2)}')

        stats.extend(['' for i in range(len(field)-len(stats))])

        result = [x + y for x, y in zip(field, stats)]


        return '\n'.join(result)
    

    def save(self):
        return Field([x[::] for x in self.logic][::])