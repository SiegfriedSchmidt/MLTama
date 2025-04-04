import socketio
import uvicorn
import asyncio

from lib.init import ssl_keyfile, ssl_certfile, server_host, server_port
from lib.logger import setup_uvicorn_logger, main_logger
from lib.sio_server.server import sio


# nest_asyncio.apply()


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
