from typing import Callable, Awaitable

from lib.fen import fen_to_field, field_to_fen, piece_to_char, fen_to_side
from lib.game_mover import GameMover
from lib.player import Player
from lib.sio_server.types import SelectData, MoveData

fens = [
    '8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w',
    '8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w',  # check king capturing backwards
    '8/wwwwwwww/wwwww2w/7w/2b3b1/bb1bbbbb/2bWb3/8/ w' # 1081 sequence
]


class Game:
    def __init__(self, fen: str, emit_select: Callable[[SelectData], Awaitable[None]],
                 emit_move: Callable[[MoveData], Awaitable[None]]):
        fen = fen if fen else fens[2]
        self.mover = GameMover(fen_to_field(fen), fen_to_side(fen))
        self.players: list[Player] = []
        self.emit_select = emit_select
        self.emit_move = emit_move
        self.selected: SelectData | None = None

    @property
    def fen(self) -> str:
        return field_to_fen(self.mover.field, self.mover.side)

    async def click(self, row: int, col: int) -> None:
        if not await self.move(row, col):
            await self.select(row, col)

    async def select(self, row: int, col: int) -> None:
        if self.selected is not None and self.selected['select'] == (row, col):
            return

        possible = self.mover.get_possible_for_piece(row, col)
        print(possible)
        if not possible:
            return

        self.selected: SelectData = {'select': (row, col), 'piece': piece_to_char[self.mover.field[row, col]],
                                     'highlight': possible}
        await self.emit_select(self.selected)

    async def move(self, row: int, col: int) -> bool:
        if self.selected is None:
            return False

        move = self.selected['select'][0], self.selected['select'][1], row, col
        if not self.mover.is_move_possible(*move):
            return False

        moves = self.mover.move(*move)
        self.selected = None
        await self.emit_move(moves)
        return True
