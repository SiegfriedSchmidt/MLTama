from socketio import AsyncServer
from lib.tama.fen import fen_to_field, field_to_fen, piece_to_char, fen_to_side
from lib.tama.rules import show_possible_for_piece, get_possible_moves, is_possible_move, make_move, print_moves


class Game:
    def __init__(self, fen: str, room: str, sio: AsyncServer):
        self.field = fen_to_field(fen)
        self.side = fen_to_side(fen)
        self.moves = get_possible_moves(self.field, self.side)
        self.room = room
        self.sio = sio
        self.selected: tuple[int, int] | None = None

    @property
    def fen(self):
        return field_to_fen(self.field, self.side)

    def select(self, row: int, col: int) -> tuple[str, tuple[int, int], list[tuple[int, int]]]:
        if self.selected == (row, col):
            return '', (0, 0), [(0, 0)]

        possible = show_possible_for_piece(row, col, self.moves)
        print(possible)
        if possible:
            self.selected = row, col
            return piece_to_char[self.field[self.selected]], self.selected, possible
        else:
            return '', (0, 0), [(0, 0)]

    def move(self, row: int, col: int) -> tuple[str, str, str, tuple[int, int, int, int]]:
        if not self.selected:
            return '', '', '', (0, 0, 0, 0)

        change_side = self.moves[0, 1] <= 1
        move_idx = is_possible_move(*self.selected, row, col, self.moves)
        if move_idx:
            move = (self.selected[0], self.selected[1], row, col)
            piece = self.field[self.selected]

            self.field[self.selected] = 0
            start_fen = self.fen
            self.field[self.selected] = piece

            make_move(move_idx, self.field, moves)
            end_fen = self.fen

            self.selected = None
            if change_side:
                self.side *= -1
            return piece_to_char[piece], start_fen, end_fen, move
        else:
            return '', '', '', (0, 0, 0, 0)
