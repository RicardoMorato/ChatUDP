from socket import *

from common.constants import (
    CLOSE_CLIENT_SOCKET_MESSAGE,
    MESSAGE_CHUNK_SIZE,
)
from message_serializer.serializer import MessageSerializer


class Client:
    def __init__(self, server_port: int, server_host: str = "localhost") -> None:
        self.server_address = (server_host, server_port)

        self.socket = socket(AF_INET, SOCK_DGRAM)

        host, port = self.socket.getsockname()
        self.messages_file_name = f"{host}-{port}"

        self.message_serializer = MessageSerializer(chunk_size=MESSAGE_CHUNK_SIZE)

    def start(
        self,
    ) -> None:
        while True:
            message = input("Input message: ")

            if message == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.stop()

                break

            file_path = self.message_serializer.build_messages_file(
                file_name=self.messages_file_name, message=message
            )

            chunked_message = self.message_serializer.parse_file_into_message_stream(
                file_path
            )

            for chunk in chunked_message:
                self.socket.sendto(chunk.encode(), self.server_address)

            self.message_serializer.remove_file(self.messages_file_name)

            received_message, _ = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)

            print(f"[CLIENT] Received message: {received_message.decode()}")

    def stop(self) -> None:
        print("[CLIENT] Closing socket connection")

        self.socket.close()
