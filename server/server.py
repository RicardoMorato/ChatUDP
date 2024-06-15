from socket import *

from common.constants import (
    FINISH_SERVER_MESSAGE,
    MESSAGE_CHUNK_SIZE,
)


class Server:
    def __init__(self, port: int, host: str = "localhost") -> None:
        self.address = (host, port)
        self.clients = []
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind(self.address)

        print("[SERVER] The server is ready to receive messages")

        while True:
            chunk_message, client_address = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)

            received_chunk_message = chunk_message.decode()
            greeting_message = "hi, meu nome eh "

            if received_chunk_message.startswith(greeting_message):
                client_name = received_chunk_message.split(greeting_message)[1]

                client = {"address": client_address, "name": client_name}

                self.clients.append(client)

                connected_successfully = "You connected successfully to the chat"

                self.socket.sendto(connected_successfully.encode(), client_address)

                print(f"[SERVER] Client was added to the clients list: {client}")
                print(f"[SERVER] Current clients list: {self.clients}")

            print(
                f"[SERVER] Received the following chunk from client {client_address}: {received_chunk_message}. "
                "And will broadcast to the others"
            )

            print(f"[SERVER] Current clients list: {self.clients}")

            for client in self.clients:
                if client_address != client["address"]:
                    self.socket.sendto(
                        received_chunk_message.encode(), client["address"]
                    )
