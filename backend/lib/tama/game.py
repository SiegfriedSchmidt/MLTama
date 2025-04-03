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

    async def click(self, row: int, col: int) -> None:
        if not await self.move(row, col):
            await self.select(row, col)

    async def select(self, row: int, col: int) -> None:
        if self.player_side != self.mover.side:
            return

        if self.selected == (row, col):
            return

        possible = self.mover.get_possible_for_piece(row, col)
        print(possible)
        if not possible:
            return

        self.selected = row, col
        await self.sio.emit(
            'select',
            {'select': self.selected, 'piece': piece_to_char[self.mover.field[*self.selected]], 'highlight': possible},
            room=self.room
        )

    async def move(self, row: int, col: int) -> bool:
        if not self.selected:
            return False

        move = self.selected[0], self.selected[1], row, col
        if not self.mover.is_move_possible(*move):
            return False

        piece = self.mover.field[self.selected]

        self.mover.field[self.selected] = 0
        start_fen = self.fen
        self.mover.field[self.selected] = piece

        self.mover.move(*move)
        end_fen = self.fen

        self.selected = None
        await self.sio.emit(
            'move', {'move': move, 'piece': piece_to_char[piece], 'fenStart': start_fen, 'fenEnd': end_fen},
            room=self.room
        )

        return True
