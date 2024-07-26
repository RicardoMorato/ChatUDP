import sys
import os
from socket import *
from typing import Any
from datetime import datetime

# Adicionando o diretório pai ao sys.path para nao ter erro de importação do modulo common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.constants import (
    MESSAGE_CHUNK_SIZE,
    GREETING_MESSAGE,
    USER_JOINED_THE_ROOM_MESSAGE,
    USER_CONNECTED_SUCCESSFULLY_MESSAGE,
    CLOSE_CLIENT_SOCKET_MESSAGE,
    USER_LEFT_THE_ROOM_MESSAGE,
    ACK_MESSAGE
)

class Server:
    def __init__(self, port: int, host: str = "localhost") -> None:
        self.address = (host, port)
        self.clients = []
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.sequence_numbers = {}  # Armazena o número de sequência do cliente

    def start(self) -> None:
        self.socket.bind(self.address)
        print("[SERVER] The server is ready to receive messages")

        while True:
            chunk_message, client_address = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)
            received_chunk_message = chunk_message.decode()
            seq_num, message = self.parse_message_with_seq(received_chunk_message)

            # Responder com ACK
            self.socket.sendto(f"{ACK_MESSAGE}{seq_num}".encode(), client_address)

            # Processar a mensagem conforme o protocolo
            self.process_message(message, client_address)

    def process_message(self, message_chunk: str, client_address) -> None:
        is_greeting_message = message_chunk.startswith(GREETING_MESSAGE)
        is_client_connected = self.is_client_already_connected(client_address)

        if is_greeting_message and not is_client_connected:
            client_name = message_chunk.split(GREETING_MESSAGE)[1]
            client = {"address": client_address, "name": client_name}
            self.clients.append(client)
            self.socket.sendto(USER_CONNECTED_SUCCESSFULLY_MESSAGE.encode(), client_address)
            client_joined_message = client_name + USER_JOINED_THE_ROOM_MESSAGE
            self.broadcast(client_address, client_joined_message)
            print(f"[SERVER] Client was added to the clients list: {client}")
            print(f"[SERVER] Current clients list: {self.clients}")
        elif is_client_connected:
            if message_chunk == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.remove_client(client_address)
            else:
                print(f"[SERVER] Received the following chunk from client {client_address}: {message_chunk}. "
                      "And will broadcast to the others")
                print(f"[SERVER] Current clients list: {self.clients}")
                message_sender = self.find_connected_client(client_address)
                messages = self.get_formatted_message(message_sender, message_chunk)
                for message in messages:
                    self.broadcast(message_sender["address"], message)

    def remove_client(self, client_address) -> None:
        client = self.find_connected_client(client_address)
        if client:
            self.clients.remove(client)
            notification = f"{client['name']}" + USER_LEFT_THE_ROOM_MESSAGE
            self.broadcast(client_address, notification)
            print(f"[SERVER] Client {client} has left the chat.")
            print(f"[SERVER] Current clients list: {self.clients}")

    def broadcast(self, sender_address, message_to_broadcast: str = "") -> None:
        for client in self.clients:
            if client["address"] != sender_address:
                self.socket.sendto(message_to_broadcast.encode(), client["address"])

    def find_connected_client(self, client_address) -> dict[str, Any]:
        for client in self.clients:
            if client["address"] == client_address:
                return client

    def is_client_already_connected(self, client_address) -> bool:
        for client in self.clients:
            if client["address"] == client_address:
                return True
        return False

    def get_formatted_message(self, message_sender: dict[str, Any], message_chunk: str) -> list[str]:
        sender_host, sender_port = message_sender["address"]
        sender_name = message_sender["name"]
        formatted_date = self.get_formatted_date_string()
        formatted_message = f"{sender_host}:{sender_port}/~{sender_name}: {message_chunk} {formatted_date}"

        if len(formatted_message) > MESSAGE_CHUNK_SIZE:
            messages = []
            formatted_message_default_length = len(f"{sender_host}:{sender_port}/~{sender_name}:  {formatted_date}")
            message_max_size = MESSAGE_CHUNK_SIZE - formatted_message_default_length - 3
            chunks = [message_chunk[i: i + message_max_size] for i in range(0, len(message_chunk), message_max_size)]
            for chunk in chunks:
                messages.append(f"{sender_host}:{sender_port}/~{sender_name}: {chunk} {formatted_date}")
            return messages
        return [formatted_message]

    def get_formatted_date_string(self) -> str:
        current_date = datetime.now()
        formatted_date = current_date.strftime("%H:%M:%S %d/%m/%Y")
        return formatted_date

    def parse_message_with_seq(self, message):
        # Implementa lógica para analisar mensagem com número de sequência
        if message.startswith("SEQ"):
            seq_num, msg = message[3:].split(":", 1)
            return int(seq_num), msg
        return -1, message  # O padrão é -1 se o número de sequência não tiver presente

