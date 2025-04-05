from typing import Callable, Awaitable

from lib.fen import fen_to_field, field_to_fen, piece_to_char, fen_to_side
from lib.game_mover import GameMover
from lib.player import HumanPlayer, ComputerPlayer
from lib.sio_server.types import SelectData, MoveData

fens = [
    '8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w',
    '8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w',  # check king capturing backwards
    '8/wwwwwwww/wwwww2w/7w/2b3b1/bb1bbbbb/2bWb3/8/ w',  # 1081 sequence
    'b4B2/2W5/8/3w1w2/8/8/w2w1w1w/1W2w1w1/ b',  # 1937 sequence
    'w1w1w1w1/w2w1b1w/8/4b1b1/2w5/1b1bw2b/b1b1b1b1/1b1b1b1b/ w',  # 4798 sequence
    'w5w1/3w4/4b3/3b4/6B1/1bwb1b2/b1b1b1b1/1b1b1b1b/ w',  # 6189 sequence
    '8/wwwwwwww/1w2wwww/w1ww4/b7/bbbbbbbb/1bbbbbbb/8/ w',  # error
]


class Game:
    def __init__(self, fen: str, emit_select: Callable[[SelectData], Awaitable[None]],
                 emit_move: Callable[[MoveData], Awaitable[None]]):
        fen = fen if fen else fens[6]
        self.mover = GameMover(fen_to_field(fen), fen_to_side(fen))
        self.human_players: dict[str, HumanPlayer] = {}
        self.computer_players: dict[int, ComputerPlayer] = {-1: ComputerPlayer(-1, 6)}
        self.emit_select = emit_select
        self.emit_move = emit_move
        self.selected: SelectData | None = None

    @property
    def fen(self) -> str:
        return field_to_fen(self.mover.field, self.mover.side)

    def add_human_player(self, player: HumanPlayer):
        self.human_players[player.sid] = player

    def remove_human_player(self, sid: str):
        del self.human_players[sid]

    def add_computer_player(self, player: ComputerPlayer):
        self.computer_players[player.side] = player

    async def click(self, sid: str, row: int, col: int) -> None:
        if sid not in self.human_players or self.human_players[sid].side != self.mover.side:
            return

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
        await self.computer_move()

        return True

    async def computer_move(self):
        def callback(val):
            print(f'callback {val}')

        if self.mover.side in self.computer_players:
            best_idx = await self.computer_players[self.mover.side].get_best_move(self.mover.field, callback)
            await self.emit_move(self.mover.move_by_idx(best_idx))
            await self.computer_move()
