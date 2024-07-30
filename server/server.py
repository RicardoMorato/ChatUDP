import sys
import os
from socket import *
from typing import Any
from datetime import datetime

# Adicionando o diretório pai ao sys.path para nao ter erro de importação do modulo common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from checksum.checksum import extract_data_and_checksum, verify_checksum
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
import json  # importar a biblioteca json para manipular uma biblioteca em bits
import base64


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
            pacote, client_address = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)

            received_packet = json.loads(pacote.decode())
            num_seq = received_packet.get("seq_num")

            message_with_checksum = base64.b64decode(
                received_packet["message_with_checksum"]
            )
            message, checksum = extract_data_and_checksum(message_with_checksum)
            is_checksum_valid = verify_checksum(message, checksum)
            expected_seq_num = self.sequence_numbers.get(client_address, 0)
            # Se o pacote chegar, vai sempre incrementar o número de sequência esperado, se não chegar, segue a logica de reenvio
            if num_seq == 0:
                self.expected_sequence_numbers_soma += 1
            else:
                self.expected_sequence_numbers_soma += num_seq
            # print(f"Valor atual: {self.expected_sequence_numbers_soma}")

            self.sequence_numbers_soma += 1
            # print(f"Valor atual: {self.sequence_numbers_soma}")

            if not is_checksum_valid:
                self.socket.sendto(f"{NACK_MESSAGE}{num_seq}".encode(), client_address)
                raise ValueError("Checksum inválido")

            else:
                # Verifica se o número de sequencia esta correto

                if (
                    num_seq == expected_seq_num
                    or self.sequence_numbers_soma == self.expected_sequence_numbers_soma
                ):
                    # Atualiza o número de sequência esperado para o próximo pacote
                    self.sequence_numbers[client_address] = (expected_seq_num + 1) % 2
                    self.socket.sendto(
                        f"{ACK_MESSAGE}{num_seq}".encode(), client_address
                    )  # Só manda o ACK para o cliente se o checksum for válido
                    self.process_message(message.decode(), client_address)
                else:
                    print("Pacote fora de ordem.")

    def process_message(self, message_chunk: str, client_address) -> None:
        # Usuário mandou a mensagem de saudação
        is_greeting_message = message_chunk.startswith(GREETING_MESSAGE)
        is_client_connected = self.is_client_already_connected(client_address)

        if is_greeting_message and not is_client_connected:
            client_name = message_chunk.split(GREETING_MESSAGE)[1]
            client = {"address": client_address, "name": client_name}
            self.clients.append(client)
            self.socket.sendto(
                USER_CONNECTED_SUCCESSFULLY_MESSAGE.encode(), client_address
            )
            # Enviando mensagem "Fulano entrou na sala"
            client_joined_message = client_name + USER_JOINED_THE_ROOM_MESSAGE
            self.broadcast(client_address, client_joined_message)
            print(f"[SERVER] Client was added to the clients list: {client}")
            print(f"[SERVER] Current clients list: {self.clients}")
        elif is_client_connected:
            if message_chunk == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.remove_client(client_address)
            else:
                print(
                    f"[SERVER] Received the following chunk from client {client_address}: {message_chunk}. "
                    "And will broadcast to the others"
                )
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

    def get_formatted_message(
        self, message_sender: dict[str, Any], message_chunk: str
    ) -> list[str]:
        sender_host, sender_port = message_sender["address"]
        sender_name = message_sender["name"]
        formatted_date = self.get_formatted_date_string()
        formatted_message = f"{sender_host}:{sender_port}/~{sender_name}: {message_chunk} {formatted_date}"

        if len(formatted_message) > MESSAGE_CHUNK_SIZE:
            """
            Se entrarmos nessa condição, significa que a mensagem formatada (host + message_chunk + timestamp)
            é maior do que o chunk_size pré-determinado enviado pelo socket.
            Portanto, precisamos dividir a o message_chunk em chunks menores que respeitem o MESSAGE_CHUNK_SIZE.
            """
            messages = []
            formatted_message_default_length = len(
                f"{sender_host}:{sender_port}/~{sender_name}:  {formatted_date}"
            )
            message_max_size = MESSAGE_CHUNK_SIZE - formatted_message_default_length - 3
            chunks = [
                message_chunk[i : i + message_max_size]
                for i in range(0, len(message_chunk), message_max_size)
            ]
            for chunk in chunks:
                messages.append(
                    f"{sender_host}:{sender_port}/~{sender_name}: {chunk} {formatted_date}"
                )
            return messages
        return [formatted_message]

    def get_formatted_date_string(self) -> str:
        current_date = datetime.now()
        formatted_date = current_date.strftime("%H:%M:%S %d/%m/%Y")
        return formatted_date


"""
    def parse_message_with_seq(self, message):
        # analisar o número de sequência
        if message.startswith("SEQ"):
            seq_num, msg = message[3:].split(":", 1)
            return int(seq_num), msg
        return -1, message  # O padrão é -1 se o número de sequência não tiver presente
"""
