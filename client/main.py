from client.client import Client
from common.constants import (
    SERVER_HOST,
    SERVER_PORT,
)

client = Client(SERVER_PORT, SERVER_HOST)

client.start()
