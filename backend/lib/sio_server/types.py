from typing import Literal, TypedDict

# ------------------
# Clients to server
# ------------------

ServerStatusType = Literal['success', 'warning', 'error']


class ClientStartData(TypedDict):
    room: str
    fen: str
    restart: bool


class ClientStartCallback(TypedDict):
    status: ServerStatusType


# ------------------
# Server to clients
# ------------------

class SelectData(TypedDict):
    select: tuple[int, int]
    piece: str
    highlight: list[int, int]


class MoveData(TypedDict):
    move: tuple[int, int, int, int]
    piece: str
    fenStart: str
    fenEnd: str


class InfoData(TypedDict):
    side: int
    depth: int
    value: int
    victoryIn: int


class WinData(TypedDict):
    winner: int


class ServerStartData(TypedDict):
    room: str
    fen: str
