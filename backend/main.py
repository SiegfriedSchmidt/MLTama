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


@sio.event
async def start(sid, data):
    room = data if data else uuid()

    clients[sid].room = room

    if room in games:
        game = games[room]
        print(f'Connect to existing room {room}')
    else:
        game = Game('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w', room, sio)
        games[room] = game
        print(f'Start game in room: {room}')

    await sio.enter_room(sid, room)
    return {
        'status': 'success',
        'room': room,
        'fen': game.fen
    }


@sio.event
async def click(sid, data):
    room = clients[sid].room
    game = games[room]

    if game.selected:
        piece, fen_start, fen_end, move = game.move(*data)
        if piece:
            return await sio.emit('move', {'move': move, 'piece': piece, 'fenStart': fen_start, 'fenEnd': fen_end},
                                  room=room)

    piece, select, highlight = game.select(*data)
    if piece:
        return await sio.emit('select', {'select': select, 'piece': piece, 'highlight': highlight}, room=room)


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
