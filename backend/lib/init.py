import os

server_host = os.environ.get("HOST", "192.168.2.200")
server_port = int(os.environ.get("PORT", 5000))
ssl_certs = bool(os.environ.get("SSL_CERTS", True))
production = os.environ.get("ENVIRONMENT", "development") == "production"
ssl_keyfile = os.environ.get("SSL_KEYFILE", '../certs/server-key.pem')
ssl_certfile = os.environ.get("SSL_CERTFILE", '../certs/server-cert.pem')
