import numpy as np
from socketio import AsyncServer

from lib.tama.fen import convert_fen_to_field, convert_field_to_fen, piece_to_char


class Game:
    def __init__(self, fen: str, room: str, sio: AsyncServer):
        self.field = convert_fen_to_field(fen)
        self.room = room
        self.sio = sio
        self.selected: tuple[int, int] | None = None

    @property
    def fen(self):
        return convert_field_to_fen(self.field, True)

    def select(self, row: int, col: int) -> tuple[str, tuple[int, int], list[tuple[int, int]]]:
        if self.field[row, col] > 0:
            if self.selected == (row, col):
                return '', (0, 0), [(0, 0)]

            self.selected = row, col
            return piece_to_char[self.field[row, col]], (row, col), [(row - 1, col - 1), (row - 1, col),
                                                                     (row - 1, col + 1)]
        else:
            return '', (0, 0), [(0, 0)]

    def move(self, row: int, col: int) -> tuple[str, str, str, tuple[int, int, int, int]]:
        if self.selected and self.field[row, col] <= 0:
            move = (self.selected[0], self.selected[1], row, col)
            piece = self.field[*self.selected]

            self.field[*self.selected] = 0
            start_fen = self.fen

            self.field[row, col] = piece
            end_fen = self.fen

            self.selected = None
            return piece_to_char[self.field[row, col]], start_fen, end_fen, move
        else:
            return '', '', '', (0, 0, 0, 0)
