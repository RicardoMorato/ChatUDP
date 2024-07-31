import sys
import os
import json
from socket import *
from typing import Any
from datetime import datetime

# Adicionando o diretório pai ao sys.path para nao ter erro de importação do modulo common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from checksum.checksum import (
    extract_data_and_checksum,
    get_message_checksum,
    verify_checksum,
)
from common.constants import (
    MESSAGE_CHUNK_SIZE,
    GREETING_MESSAGE,
    USER_JOINED_THE_ROOM_MESSAGE,
    USER_CONNECTED_SUCCESSFULLY_MESSAGE,
    CLOSE_CLIENT_SOCKET_MESSAGE,
    USER_LEFT_THE_ROOM_MESSAGE,
    ACK_MESSAGE,
    NACK_MESSAGE,
)


class Server:
    def __init__(self, port: int, host: str = "localhost") -> None:
        self.address = (host, port)
        self.clients = []
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.sequence_numbers = {}  # armazena o número de sequência do cliente
        self.expected_sequence_numbers_soma = 0
        self.sequence_numbers_soma = 0

    def start(self) -> None:
        self.socket.bind(self.address)
        print("[SERVER] The server is ready to receive messages")

        while True:
            packet, client_address = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)

            received_packet = json.loads(packet.decode())

            seq_num: int = received_packet.get("seq_num")
            checksum: str = received_packet.get("checksum")
            message: str = received_packet.get("message")

            is_checksum_valid = verify_checksum(message.encode(), checksum)

            expected_seq_num = self.sequence_numbers.get(client_address, 0)
            is_seq_num_valid = expected_seq_num == seq_num

            data = {
                "checksum": get_message_checksum(ACK_MESSAGE.encode()),
                "seq_num": expected_seq_num,
                "message": ACK_MESSAGE,
            }

            if not is_checksum_valid:
                print(
                    f"[SERVER] Client with address {client_address} has sent a packet with an invalid checksum."
                )
                # ENVIA NACK
                self.socket.sendto(json.dumps(data).encode(), client_address)
                continue

            if not is_seq_num_valid:
                print(
                    f"[SERVER] Client with address {client_address} has sent a packet with an invalid seq number."
                )
                # ENVIA NACK
                self.socket.sendto(json.dumps(data).encode(), client_address)
                continue

            # Atualiza o número de sequência esperado para o próximo pacote
            self.sequence_numbers[client_address] = (expected_seq_num + 1) % 2

            self.socket.sendto(json.dumps(data).encode(), client_address)

            self.process_message(message, client_address)

    def process_message(self, message_to_send: str, client_address) -> None:
        # Usuário mandou a mensagem de saudação
        is_greeting_message = message_to_send.startswith(GREETING_MESSAGE)
        is_client_connected = self.is_client_already_connected(client_address)

        if is_greeting_message and not is_client_connected:
            client_name = message_to_send.split(GREETING_MESSAGE)[1]
            client = {"address": client_address, "name": client_name}
            self.clients.append(client)

            message_metadata = self.get_message_metadata(client)

            encapsulated_message = {
                "message": USER_CONNECTED_SUCCESSFULLY_MESSAGE,
                **message_metadata,
            }

            self.socket.sendto(
                json.dumps(encapsulated_message).encode(), client_address
            )

            # Enviando mensagem "Fulano entrou na sala"
            client_joined_message = client_name + USER_JOINED_THE_ROOM_MESSAGE

            encapsulated_message["message"] = client_joined_message
            self.broadcast(client_address, encapsulated_message)

            print(f"[SERVER] Client was added to the clients list: {client}")
            print(f"[SERVER] Current clients list: {self.clients}")
        elif is_client_connected:
            if message_to_send == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.remove_client(client_address)
            else:
                print(
                    f"[SERVER] Received the following chunk from client {client_address}: "
                    f"{message_to_send}. "
                    "And will broadcast to the others"
                )
                print(f"[SERVER] Current clients list: {self.clients}")
                message_sender = self.find_connected_client(client_address)

                message_metadata = self.get_message_metadata(message_sender)

                encapsulated_message = {
                    "message": message_to_send,
                    **message_metadata,
                }

                self.broadcast(message_sender["address"], encapsulated_message)

    def remove_client(self, client_address) -> None:
        client = self.find_connected_client(client_address)
        if client:
            self.clients.remove(client)
            notification = f"{client['name']}" + USER_LEFT_THE_ROOM_MESSAGE

            message_metadata = self.get_message_metadata(client)

            encapsulated_message = {"message": notification, **message_metadata}

            self.broadcast(client_address, encapsulated_message)
            print(f"[SERVER] Client {client} has left the chat.")
            print(f"[SERVER] Current clients list: {self.clients}")

    def broadcast(
        self,
        sender_address,
        data: dict[str, str] = {},
    ) -> None:
        for client in self.clients:
            if client["address"] != sender_address:
                print(
                    f"[SERVER] Broadcasting the following message and headers: ",
                    data,
                )

                self.socket.sendto(json.dumps(data).encode(), client["address"])

    def find_connected_client(self, client_address) -> dict[str, Any]:
        for client in self.clients:
            if client["address"] == client_address:
                return client

    def is_client_already_connected(self, client_address) -> bool:
        for client in self.clients:
            if client["address"] == client_address:
                return True
        return False

    def get_message_metadata(self, message_sender: dict[str, Any]) -> dict[str, str]:
        sender_host, sender_port = message_sender["address"]
        sender_name = message_sender["name"]
        formatted_date = self.get_formatted_date_string()

        metadata = {
            "time": formatted_date,
            "sender_info": f"{sender_host}:{sender_port}/~{sender_name}",
        }

        return metadata

    def get_formatted_date_string(self) -> str:
        current_date = datetime.now()
        formatted_date = current_date.strftime("%H:%M:%S %d/%m/%Y")
        return formatted_date
