import numpy as np

from lib.fen import field_to_fen, piece_to_char
from lib.sio_server.types import MoveData
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

    def __get_move_from_idx(self, i):
        return map(int, [*self.moves[i, 2:4], *self.moves[i + 1, 2:4]]) if self.moves[0, 1] else map(int, [
            *self.moves[i, 0:4]])

    def __add_index_to_possible(self, i):
        row, col, row2, col2 = self.__get_move_from_idx(i)

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

    def __create_move_data(self, i: int, capture: bool, is_side_changes: bool) -> MoveData:
        row, col, row2, col2 = self.__get_move_from_idx(i)
        piece = self.field[row, col]

        self.field[row, col] = 0
        fen_start = field_to_fen(self.field, self.side)
        self.field[row, col] = piece

        if capture:
            make_move_with_capture(self.field, *self.moves[i, 2:4], *self.moves[i + 1])
        else:
            make_move_without_capture(self.field, *self.moves[i])

        fen_end = field_to_fen(self.field, -self.side if is_side_changes else self.side)
        return {'piece': piece_to_char[piece], 'move': (row, col, row2, col2), 'fenStart': fen_start, 'fenEnd': fen_end}

    def raw_move(self, move_idx: int, capture_len: int, is_side_changes=True) -> list[MoveData]:
        moves: list[MoveData] = []
        if capture_len:
            for i in range(move_idx, move_idx + capture_len):
                moves.append(self.__create_move_data(i, True, is_side_changes and i == move_idx + capture_len - 1))
        else:
            moves.append(self.__create_move_data(move_idx, False, True))

        return moves

    def move_by_idx(self, move_idx: int):
        moves = self.raw_move(move_idx, self.moves[0, 1])
        self.__end_move()
        return moves

    def move(self, from_row, from_col, to_row, to_col):
        move_idx = self.readable_moves[from_row, from_col][to_row, to_col][0]
        if self.cur_capture < self.moves[0, 1]:
            move = self.raw_move(move_idx, self.cur_capture + 1 == self.moves[0, 1])

            self.cur_capture += 1
            if self.cur_capture == self.moves[0, 1]:
                self.__end_move()
            else:
                self.__fill_readable_moves(self.readable_moves[from_row, from_col][to_row, to_col])
        else:
            move = self.raw_move(move_idx, 0)
            self.__end_move()
        return move

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
