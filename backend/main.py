import socketio
import uvicorn
import asyncio

from lib.client_data import ClientData
from lib.init import ssl_keyfile, ssl_certfile
from lib.init import server_host, server_port
from lib.logger import setup_uvicorn_logger, main_logger
from lib.tama.game import Game
from lib.utils.uuid import uuid

# nest_asyncio.apply()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

games: dict[str, Game] = {}
clients: dict[str, ClientData] = {}


@sio.event
async def connect(sid, environ, auth):
    clients[sid] = ClientData(sid)
    print('connect ', sid)


@sio.event
async def disconnect(sid):
    clients.pop(sid)
    print('disconnect ', sid)


async def connect_to_room(sid, room, fen):
    room = room if room else uuid()  # check if client wants specific or random
    clients[sid].room = room
    await sio.enter_room(sid, room)
    if room in games:
        # existing room
        print(f'enter existing room {room}')
        game = games[room]
    else:
        # new room
        print(f'create new room {room}')
        game = Game(fen, room, sio)
        games[room] = game

    return await sio.emit('start', {'room': room, 'fen': game.fen}, to=sid)


@sio.event
async def start(sid, data):
    if clients[sid].room and clients[sid].room in games:
        # already have room
        room = clients[sid].room
        if data['restart']:
            print(f'restart game in room {room}')
            del games[room]
            game = Game(data['fen'], room, sio)
            games[room] = game
            await sio.emit('start', {'room': room, 'fen': game.fen}, room=room)
        else:
            # want to join to other room
            await sio.leave_room(sid, room)
            await connect_to_room(sid, data['room'], data['fen'])

        return {'status': 'success'}

    if data['restart']:
        return {'status': 'error'}

    await connect_to_room(sid, data['room'], data['fen'])
    return {'status': 'success'}


@sio.event
async def click(sid, data):
    room = clients[sid].room
    if not room or room not in games:
        return

    await games[room].click(*data)


async def makeOpponentMove(data):
    # task = asyncio.create_task(makeOpponentMove(data))
    await asyncio.sleep(3)
    await sio.emit('opponentMove', {'move': '', 'fen': ''}, room='game')


async def main():
    setup_uvicorn_logger()

    app = socketio.ASGIApp(sio)
    server = uvicorn.Server(uvicorn.Config(
        app,
        host=server_host,
        port=server_port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        log_level="debug",
        log_config=None,
        workers=1
    ))
    await server.serve()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        main_logger.info('Server successfully exited.')
