from socket import *

from common.constants import (
    FINISH_SERVER_MESSAGE,
    MESSAGE_CHUNK_SIZE,
    SERVER_HOST,
    SERVER_PORT,
)

server_socket = socket(AF_INET, SOCK_DGRAM)

server_socket.bind((SERVER_HOST, SERVER_PORT))

print("[SERVER] The server is ready to receive messages")

while True:
    message, client_address = server_socket.recvfrom(MESSAGE_CHUNK_SIZE)

    received_message = message.decode()

    print(
        f"[SERVER] Received the following message from client {client_address}: {received_message}"
    )

    server_socket.sendto(received_message.encode(), client_address)

    if received_message == FINISH_SERVER_MESSAGE:
        print(
            "[SERVER] The server has received the finish message. Will exit the process."
        )
        break
