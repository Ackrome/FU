import sys
import random

class Game:
    def __init__(self):
        self.board = Board()
        self.turn = "white"
        self.moves = 0

    def get_move(self):
        if self.turn == "white":
            color = "белыми"
        else:
            color = "черными"
        print(f"Ход {color}. Введите позицию фигуры для следующего хода:")
        position = input()
        while not self.is_valid_position(position):
            print("Некорректная позиция. Введите позицию фигуры для следующего хода:")
            position = input()
        print(f"Ход {color}. Введите целевую позицию выбранной фигуры:")
        target = input()
        while not self.is_valid_target(position, target):
            print("Некорректная целевая позиция. Введите целевую позицию выбранной фигуры:")
            target = input()
        return position, target

    def is_valid_position(self, position):
        if len(position) != 2:
            return False
        if not position[0].isalpha() or not position[1].isdigit():
            return False
        return 0 <= int(position[1]) <= 7 and "a" <= position[0] <= "h"

    def is_valid_target(self, position, target):
        piece = self.board.get_piece_at(position)
        if piece is None:
            return False
        if piece.color != self.turn:
            return False
        if not piece.can_move_to(target):
            return False
        return True

    def make_move(self, position, target):
        self.board.move(position, target)
        self.turn = "black" if self.turn == "white" else "white"
        self.moves += 1

    def check_mate(self):
        for color in ["white", "black"]:
            for piece in self.board.pieces_of_color(color):
                if piece.can_move_to(piece.position):
                    return False
        return True

    def print_board(self):
        for row in self.board.rows:
            print(" ".join([piece.symbol if piece is not None else " " for piece in row]))

    def run(self):
        while not self.check_mate():
            self.print_board()
            position, target = self.get_move()
            self.make_move(position, target)

if __name__ == "__main__":
    game = Game()
    game.run()
