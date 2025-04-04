import os

server_host = os.environ.get("HOST", "192.168.2.200")
server_port = int(os.environ.get("PORT", 5000))
ssl_keyfile = os.environ.get("SSL_KEYFILE", '../certs/server-key.pem')
ssl_certfile = os.environ.get("SSL_CERTFILE", '../certs/server-cert.pem')
