import numpy as np
from socketio import AsyncServer

from lib.tama.fen import convert_fen_to_field, convert_field_to_fen


class Game:
    def __init__(self, fen: str, room: str, sio: AsyncServer):
        self.field = convert_fen_to_field(fen)
        self.room = room
        self.sio = sio
        self.selected = None

    @property
    def fen(self):
        return convert_field_to_fen(self.field, True)

    def select(self, row: int, col: int):
        if self.field[row, col] > 0:
            self.selected = row, col
            return [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1)]
        else:
            return []

    def move(self, row: int, col: int):
        if self.field[row, col] <= 0:
            move = [*self.selected, row, col]
            piece = self.field[*self.selected]

            self.field[*self.selected] = 0
            start_fen = self.fen

            self.field[row, col] = piece
            end_fen = self.fen

            self.selected = None
            return move, start_fen, end_fen
        else:
            return [], '', ''
