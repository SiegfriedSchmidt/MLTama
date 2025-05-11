import socketio
import uvicorn
import asyncio

from lib.init import ssl_keyfile, ssl_certfile, server_host, server_port, ssl_certs, production
from lib.logger import setup_uvicorn_logger, main_logger
from lib.sio_server.server import sio

# nest_asyncio.apply()

static_files = {
    '/': './dist/index.html',
    '/static': './dist',
}


async def main():
    setup_uvicorn_logger()

    app = socketio.ASGIApp(sio, static_files=static_files if production else None)
    server = uvicorn.Server(uvicorn.Config(
        app,
        host=server_host,
        port=server_port,
        ssl_keyfile=ssl_keyfile if ssl_certs else None,
        ssl_certfile=ssl_certfile if ssl_certs else None,
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
