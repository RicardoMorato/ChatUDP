import threading
import sys
import os
import time
import socket

# Adicionando o diretório pai ao sys.path para nao ter erro de importação do modulo common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.constants import (
    CLOSE_CLIENT_SOCKET_MESSAGE,
    END_OF_MESSAGE_IDENTIFIER,
    GREETING_MESSAGE,
    MESSAGE_CHUNK_SIZE,
    USER_CONNECTED_SUCCESSFULLY_MESSAGE,
    USER_JOINED_THE_ROOM_MESSAGE,
    USER_LEFT_THE_ROOM_MESSAGE,
    ACK_MESSAGE,
    NACK_MESSAGE,
)
from message_serializer.serializer import MessageSerializer
from checksum.checksum import *
import json
import base64


class Client:
    def __init__(self, server_port: int, server_host: str = "localhost") -> None:
        self.server_address = (server_host, server_port)
        self.timeout = 1  # Timeout em segundos

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)

        host, port = self.socket.getsockname()
        self.messages_file_name = f"{host}-{port}"
        self.messages_receiver_file_name = f"{self.messages_file_name}-receiver"
        self.message_serializer = MessageSerializer(chunk_size=MESSAGE_CHUNK_SIZE)
        self.sequence_number = 0
        self.lock = threading.Lock()
        self.timer = None  # Temporizador
        self.current_packet = None  # Pacote a ser reenviado

    def start(self) -> None:
        pause_event = threading.Event()
        pause_event.clear()  # Red light for the listen thread

        thread = threading.Thread(daemon=True, target=self.listen, args=(pause_event,))
        thread.start()

        while True:
            message = input("")
            pause_event.clear()  # Red light for the listen thread

            file_path = self.message_serializer.build_messages_file(
                file_name=self.messages_file_name, message=message
            )

            with open(file_path, "rb") as file:
                chunk_content = file.read(MESSAGE_CHUNK_SIZE)

                # Adiciona o checksum ao pacote
                checksum = get_message_checksum(chunk_content)

                seq_num = self.sequence_number

                data = {
                    "checksum": checksum,
                    "seq_num": seq_num,
                    "message": chunk_content.decode("utf-8"),
                }

                self.current_packet = json.dumps(data).encode()
                # self.start_timer()  # Inicia o temporizador
                self.socket.sendto(self.current_packet, self.server_address)

                while True:
                    try:
                        packet = self.socket.recv(1024)
                    except BlockingIOError:
                        """
                        Esse erro
                        """
                        continue

                    received_packet = json.loads(packet.decode())

                    received_seq_num: int = received_packet.get("seq_num")
                    received_checksum: str = received_packet.get("checksum")
                    received_message: str = received_packet.get("message")

                    is_checksum_valid = verify_checksum(
                        received_message.encode(), received_checksum
                    )

                    if (
                        not is_checksum_valid
                        or received_seq_num != self.sequence_number
                    ):
                        # TODO: RE-ENVIAR O PACOTE
                        continue

                    self.sequence_number = (received_seq_num + 1) % 2

                    if self.timer is not None:
                        self.timer.cancel()  # Para o temporizador

                    break

            pause_event.set()

            self.message_serializer.remove_file(
                self.messages_file_name
            )  # VER ONDE COLOCAR ISSO AQUI DEPOIS

            if message == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.stop()
                break

    def start_timer(self):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.timer_expired)
        self.timer.start()
        # print(f"temporizador iniciado para o numero de sequencia: {self.sequence_number}")

    def timer_expired(self):
        # Sprint(f"temporizador expirado para o numero de sequencia: {self.sequence_number}")
        self.retransmit_packet()

    def retransmit_packet(self):
        with self.lock:
            if self.current_packet:
                self.socket.sendto(self.current_packet, self.server_address)
                self.start_timer()
                # print(f"Reenviando pacote número de sequência {self.sequence_number}.")
                time.sleep(1)

    def stop(self) -> None:
        print("[CLIENT] Closing socket connection")
        if self.timer is not None:
            self.timer.cancel()
        self.socket.close()

    def listen(self, pause_event: threading.Event) -> None:
        while True:
            if pause_event.is_set():
                try:
                    received_message = self.socket.recv(MESSAGE_CHUNK_SIZE)
                    message = received_message.decode()

                    if (
                        message == USER_CONNECTED_SUCCESSFULLY_MESSAGE
                        or USER_JOINED_THE_ROOM_MESSAGE in message
                        or USER_LEFT_THE_ROOM_MESSAGE in message
                    ):
                        print(f"\n{message}")
                    else:
                        print(message)

                    # else:
                    #     message_text, host, timestamp = (
                    #         self.message_serializer.extract_parts_of_received_message(
                    #             message
                    #         )
                    #     )
                    #     if message_text != END_OF_MESSAGE_IDENTIFIER:
                    #         file_path = self.message_serializer.build_messages_file(
                    #             file_name=self.messages_receiver_file_name,
                    #             message=message_text,
                    #         )
                    #     else:
                    #         text = self.message_serializer.read_all_content_from_file(
                    #             file_path
                    #         )
                    #         print(f"\n{host}: {text} {timestamp}")
                    #         self.message_serializer.remove_file(
                    #             self.messages_receiver_file_name
                    #         )
                except BlockingIOError:
                    # print("DID NOT BLOCK I/O")
                    continue


"""
Pelo menos até o momento, as linhas 63, 70, 92, 96 e 97 (pode ser que as alterações futuras 
desça as linhas de codigo) tem prints que mostram
a ordem de saída e entrada de cada pacote, e o tempo que cada pacote
leva para ser enviado e recebido.
"""


"""Como não esta implementado o reenvio do pacote, o temporizador expira e o pacote ainda chega ao servidor
é preciso mudar essa logica (ainda esta chegando com o reenvio)
"""
