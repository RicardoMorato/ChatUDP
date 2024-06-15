from socket import *

from common.constants import (
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
            user_joined_the_room_message = " entrou na sala!"

            if received_chunk_message.startswith(greeting_message):
                client_name = received_chunk_message.split(greeting_message)[1]

                client = {"address": client_address, "name": client_name}

                self.clients.append(client)

                connected_successfully = "You connected successfully to the chat"

                # Enviando mensagem "Conectado com sucesso"
                self.socket.sendto(connected_successfully.encode(), client_address)

                client_joined_message = client_name + user_joined_the_room_message

                # Enviando mensagem "Fulano entrou na sala"
                for client in self.clients:
                    if client_address != client["address"]:
                        self.socket.sendto(
                            client_joined_message.encode(), client["address"]
                        )

                print(f"[SERVER] Client was added to the clients list: {client}")
                print(f"[SERVER] Current clients list: {self.clients}")
            else:
                print(
                    f"[SERVER] Received the following chunk from client {client_address}: {received_chunk_message}. "
                    "And will broadcast to the others"
                )

                print(f"[SERVER] Current clients list: {self.clients}")

                message_sender = [
                    c for c in self.clients if c["address"] == client_address
                ][0]

                for client in self.clients:
                    sender_host, sender_port = message_sender["address"]
                    sender_name = message_sender["name"]

                    message = f"{sender_host}:{sender_port}/~{sender_name}: {received_chunk_message}"

                    if client_address != client["address"]:
                        self.socket.sendto(message.encode(), client["address"])
