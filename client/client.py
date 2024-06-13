from socket import *

from common.constants import (
    CLOSE_CLIENT_SOCKET_MESSAGE,
    MESSAGE_CHUNK_SIZE,
    SERVER_HOST,
    SERVER_PORT,
)
from message_serializer.serializer import MessageSerializer

client_socket = socket(AF_INET, SOCK_DGRAM)

message_serializer = MessageSerializer(chunk_size=MESSAGE_CHUNK_SIZE)

tmp_file_name = "tmp_file_client"

while True:
    message = input("Input message: ")

    if message == CLOSE_CLIENT_SOCKET_MESSAGE:
        break

    file_path = message_serializer.build_messages_file(
        file_name=tmp_file_name, message=message
    )

    chunked_message = message_serializer.parse_file_into_message_stream(file_path)

    for chunk in chunked_message:
        client_socket.sendto(chunk.encode(), (SERVER_HOST, SERVER_PORT))

    message_serializer.remove_file(tmp_file_name)

    received_message, server_address = client_socket.recvfrom(MESSAGE_CHUNK_SIZE)

    print(f"[CLIENT] Received message: {received_message.decode()}")

client_socket.close()
