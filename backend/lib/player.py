class Player:
    def __init__(self, side: int):
        self.side = side  # 1 for white, -1 for black, 0 for spectator


class HumanPlayer(Player):
    def __init__(self, side: int, sid: str):
        super().__init__(side)
        self.sid = sid


class ComputerPlayer(Player):
    def __init__(self, side: int):
        super().__init__(side)
