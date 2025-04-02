from socketio import AsyncServer
from lib.tama.fen import fen_to_field, field_to_fen, piece_to_char, fen_to_side
from lib.tama.game_mover import GameMover

fens = [
    '8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w',
    '8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w'  # check king capturing backwards
]


class Game:
    def __init__(self, fen: str, room: str, sio: AsyncServer):
        fen = fen if fen else fens[0]
        self.mover = GameMover(fen_to_field(fen), fen_to_side(fen))
        self.player_side = 1
        self.room = room
        self.sio = sio
        self.selected: tuple[int, int] | None = None

    @property
    def fen(self) -> str:
        return field_to_fen(self.mover.field, self.mover.side)

    def select(self, row: int, col: int) -> tuple[str, tuple[int, int], list[tuple[int, int]]]:
        if self.player_side != self.mover.side:
            return '', (0, 0), [(0, 0)]

        if self.selected == (row, col):
            return '', (0, 0), [(0, 0)]

        possible = self.mover.get_possible_for_piece(row, col)
        print(possible)
        if possible:
            self.selected = row, col
            return piece_to_char[self.mover.field[*self.selected]], self.selected, possible
        else:
            return '', (0, 0), [(0, 0)]

    def move(self, row: int, col: int) -> tuple[str, str, str, tuple[int, int, int, int]]:
        if not self.selected:
            return '', '', '', (0, 0, 0, 0)

        move = self.selected[0], self.selected[1], row, col
        if self.mover.is_move_possible(*move):
            piece = self.mover.field[self.selected]

            self.mover.field[self.selected] = 0
            start_fen = self.fen
            self.mover.field[self.selected] = piece

            self.mover.move(*move)
            end_fen = self.fen

            self.selected = None
            return piece_to_char[piece], start_fen, end_fen, move
        else:
            return '', '', '', (0, 0, 0, 0)
