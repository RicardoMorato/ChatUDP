from socket import *

from common.constants import (
    CLOSE_CLIENT_SOCKET_MESSAGE,
    MESSAGE_CHUNK_SIZE,
    SERVER_HOST,
    SERVER_PORT,
)

client_socket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input("Input message: ")

    if message == CLOSE_CLIENT_SOCKET_MESSAGE:
        break

    client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))

    received_message, server_address = client_socket.recvfrom(MESSAGE_CHUNK_SIZE)

    print(f"[CLIENT] Received message: {received_message.decode()}")

client_socket.close()
