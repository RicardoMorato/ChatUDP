from socket import *

from common.constants import (
    FINISH_SERVER_MESSAGE,
    MESSAGE_CHUNK_SIZE,
)


class Server:
    def __init__(self, port: int, host: str = "localhost") -> None:
        self.address = (host, port)

        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind(self.address)

        print("[SERVER] The server is ready to receive messages")

        while True:
            chunk_message, client_address = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)

            received_chunk_message = chunk_message.decode()

            if received_chunk_message == FINISH_SERVER_MESSAGE:
                print(
                    "[SERVER] The server has received the finish message. Will exit the process."
                )

                break

            print(
                f"[SERVER] Received the following chunk from client {client_address}: {received_chunk_message}"
            )

            self.socket.sendto(received_chunk_message.encode(), client_address)
