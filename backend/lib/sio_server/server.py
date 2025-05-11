import socketio
from lib.client_data import ClientData
from lib.game import Game
from lib.player import HumanPlayer
from lib.sio_server.types import *
from lib.utils.uuid import uuid

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

games: dict[str, Game] = {}
clients: dict[str, ClientData] = {}


# ------------------
# Server to clients
# ------------------

async def server_select(data: SelectData, room: str):
    await sio.emit('select', data, room=room)


async def server_move(data: list[MoveData], room: str):
    await sio.emit('move', data, room=room)


async def server_info(data: InfoData, room: str):
    await sio.emit('info', data, room=room)


async def server_win(data: WinData, room: str):
    await sio.emit('win', data, room=room)


async def server_start(data: ServerStartData, to: str):
    await sio.emit('start', data, to=to)


# ------------------
# Clients to server
# ------------------

@sio.event
async def connect(sid, environ, auth) -> None:
    clients[sid] = ClientData(sid)
    print('connect ', sid)


@sio.event
async def disconnect(sid) -> None:
    clients.pop(sid)
    print('disconnect ', sid)


async def create_game(fen, room):
    return Game(fen, lambda data: server_select(data, room), lambda data: server_move(data, room),
                lambda data: server_info(data, room), lambda data: server_win(data, room))


async def connect_to_room(sid: str, room: str, fen: str) -> None:
    room = room if room else uuid()  # check if client wants specific or random
    clients[sid].room = room
    await sio.enter_room(sid, room)
    if room in games:
        # existing room
        print(f'enter existing room {room}')
        game = games[room]
        game.add_human_player(HumanPlayer(1 if len(game.human_players.keys()) == 0 else -1, sid))
    else:
        # new room
        print(f'create new room {room}')
        game = await create_game(fen, room)
        game.add_human_player(HumanPlayer(1 if len(game.human_players.keys()) == 0 else -1, sid))
        games[room] = game

    await server_start({'room': room, 'fen': game.fen}, to=sid)


@sio.event
async def start(sid, data: ClientStartData) -> ClientStartCallback:
    if clients[sid].room and clients[sid].room in games:
        # already have room
        room = clients[sid].room
        if data['restart']:
            # restart game
            print(f'restart game in room {room}')
            players = games[room].human_players.values()
            del games[room]
            game = await create_game(data['fen'], room)
            for player in players:
                game.add_human_player(player)
            games[room] = game
            await sio.emit('start', {'room': room, 'fen': game.fen}, room=room)
        else:
            # want to join to other room
            games[room].remove_human_player(sid)
            await sio.leave_room(sid, room)
            await connect_to_room(sid, data['room'], data['fen'])

        return {'status': 'success'}

    if data['restart']:
        return {'status': 'error'}

    await connect_to_room(sid, data['room'], data['fen'])
    return {'status': 'success'}


@sio.event
async def click(sid, data: tuple[int, int]) -> None:
    room = clients[sid].room
    if not room or room not in games:
        return

    await games[room].click(sid, *data)
