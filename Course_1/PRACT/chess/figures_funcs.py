from main import Cell

# Описание логики ходов фигур

def pawn_w(log, cll, new_x, new_y):
    cur_x= cll.X
    cur_y= cll.Y
    new_pos=tuple([new_x,new_y])

    maybe_poses=[]
    may_poses=[]

    # Возможные ходы без еды

    if cur_x == 6:
        maybe_poses.extend(
            tuple([cur_x - 1, cur_y]),
            tuple([cur_x - 2, cur_y]),
            tuple([cur_x - 1, cur_y + 1]),
            tuple([cur_x - 1, cur_y - 1]),
            )
    else:
        maybe_poses.extend(tuple([cur_x - 1, cur_y]),
                           tuple([cur_x - 1, cur_y + 1]),
                           tuple([cur_x - 1, cur_y - 1]),
            )
    
    for i in maybe_poses:
        if i[0] not in range(8) or i[i] not in range(8):
            may_poses.append(i)

    # Возможные ходы, когда пешка ест
    maybe_poses_eat = []
    may_poses_eat=[]
    maybe_poses_eat.extend(
            tuple([cur_x - 1, cur_y + 1]),
            tuple([cur_x - 1, cur_y - 1]))
    
    for i in maybe_poses_eat:
        if i[0] not in range(8) or i[i] not in range(8):
            may_poses_eat.append(i)
    
    if new_pos in may_poses:
        if log[new_x][new_y].figure == 0:
            log[new_x][new_y] == Cell('pawn',1,new_x,new_y)
            log[cur_x][cur_y] == Cell(0,0,cur_x,cur_y)
            return (1,log,[]) 
        else:
            return(0,0,[])
    
    elif new_pos in may_poses_eat:
        if log[new_x][new_y].figure == 2:
            eaten = log[new_x][new_y].figure()
            log[new_x][new_y] == Cell('pawn',1,new_x,new_y)
            log[cur_x][cur_y] == Cell(0,0,cur_x,cur_y)
            return (1,log, [eaten])
        else:
            return(0,0,[])
