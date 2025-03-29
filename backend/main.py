import socketio
import uvicorn
import asyncio

from lib.init import ssl_keyfile, ssl_certfile
from lib.init import server_host, server_port
from lib.logger import setup_uvicorn_logger, main_logger

# nest_asyncio.apply()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')


@sio.event
async def connect(sid, environ, auth):
    await sio.enter_room(sid, 'game')
    await sio.emit('opponentMove', {'move': '', 'fen': ''}, room='game')
    print('connect ', sid)


@sio.event
async def disconnect(sid):
    print('disconnect ', sid)


async def makeOpponentMove(data):
    await asyncio.sleep(3)
    await sio.emit('opponentMove', {'move': '', 'fen': ''}, room='game')


@sio.event
async def clientMove(sid, data):
    task = asyncio.create_task(makeOpponentMove(data))
    return {'status': 'success', 'content': ''}


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
