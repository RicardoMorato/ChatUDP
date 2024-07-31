from server.server import Server
from common.constants import (
    SERVER_HOST,
    SERVER_PORT,
)

server = Server(SERVER_PORT, SERVER_HOST)

server.start()
