import numpy as np

from lib.tama.rules import make_move_with_capture, make_move_without_capture, get_possible_moves


def print_moves(moves: np.ndarray) -> None:
    max_capture = moves[0, 1]
    print(moves[0], '\n')
    for i in range(1, moves[0, 0]):
        print(moves[i])
        if max_capture and (i - 1) % (max_capture + 1) == max_capture:
            print()


class GameMover:
    def __init__(self, field: np.ndarray, side: int):
        self.field = field
        self.side = side
        self.moves = get_possible_moves(field, side)
        self.readable_moves: dict[tuple[int, int], dict[tuple[int, int], list[int]]] = {}
        self.__fill_readable_moves([])
        self.cur_capture = 0

    def __add_index_to_possible(self, i):
        row, col, row2, col2 = map(int, [*self.moves[i, 2:4], *self.moves[i + 1, 2:4]]) if self.moves[0, 1] else \
            map(int, [*self.moves[i, 0:4]])

        if (row, col) not in self.readable_moves:
            self.readable_moves[row, col] = {}
        if (row2, col2) not in self.readable_moves[row, col]:
            self.readable_moves[row, col][row2, col2] = []

        self.readable_moves[row, col][row2, col2].append(i)

    def __fill_readable_moves(self, prev_sequences: list[int]):
        self.readable_moves = {}

        if self.moves[0, 1]:
            if prev_sequences:
                for i in prev_sequences:
                    self.__add_index_to_possible(i + 1)
            else:
                for i in range(1, self.moves[0, 0], self.moves[0, 1] + 1):
                    self.__add_index_to_possible(i)
        else:
            for i in range(1, self.moves[0, 0]):
                self.__add_index_to_possible(i)

    def __end_move(self):
        self.side *= -1
        self.moves = get_possible_moves(self.field, self.side)
        self.__fill_readable_moves([])
        self.cur_capture = 0

    def move(self, from_row, from_col, to_row, to_col):
        move_idx = self.readable_moves[from_row, from_col][to_row, to_col][0]
        if self.cur_capture < self.moves[0, 1]:
            make_move_with_capture(self.field, *self.moves[move_idx, 2:4], *self.moves[move_idx + 1])

            self.__fill_readable_moves(self.readable_moves[from_row, from_col][to_row, to_col])
            self.cur_capture += 1
            if self.cur_capture == self.moves[0, 1]:
                self.__end_move()
        else:
            make_move_without_capture(self.field, *self.moves[move_idx])
            self.__end_move()

    def get_possible_for_piece(self, from_row, from_col):
        if (from_row, from_col) not in self.readable_moves:
            return []
        return list(self.readable_moves[from_row, from_col].keys())

    def is_move_possible(self, from_row, from_col, to_row, to_col):
        if (from_row, from_col) not in self.readable_moves:
            return False
        if (to_row, to_col) not in self.readable_moves[from_row, from_col]:
            return False

        return True
