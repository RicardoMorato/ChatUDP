import threading
import sys
import os
import socket
import json

# Adicionando o diretório pai ao sys.path para nao ter erro de importação do modulo common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.constants import (
    CLOSE_CLIENT_SOCKET_MESSAGE,
    MESSAGE_CHUNK_SIZE,
    MESSAGE_CHUNK_SIZE_WITH_HEADERS,
    USER_CONNECTED_SUCCESSFULLY_MESSAGE,
    USER_JOINED_THE_ROOM_MESSAGE,
    USER_LEFT_THE_ROOM_MESSAGE,
)
from message_serializer.serializer import MessageSerializer
from checksum.checksum import *


class Client:
    def __init__(self, server_port: int, server_host: str = "localhost") -> None:
        self.server_address = (server_host, server_port)
        self.timeout = 1  # Timeout em segundos

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)  # Vamos lidar com sockets não-bloqueantes

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
                self.start_timer()  # Inicia o temporizador
                self.socket.sendto(self.current_packet, self.server_address)

                while True:
                    try:
                        packet = self.socket.recv(MESSAGE_CHUNK_SIZE)
                    except BlockingIOError:
                        """
                        Esse erro acontece quando o socket tenta realizar uma ação bloqueante.
                        Como configurado na linha 33, queremos que esse socket seja não-bloqueante.

                        Para mais informações, checar os links abaixo:
                        - https://stackoverflow.com/questions/63494625/python-are-sockets-and-recv-blocking-by-default
                        - https://stackoverflow.com/questions/7174927/when-does-socket-recvrecv-size-return
                        - https://stackoverflow.com/questions/25426447/creating-non-blocking-socket-in-python
                        - https://stackoverflow.com/questions/16745409/what-does-pythons-socket-recv-return-for-non-blocking-sockets-if-no-data-is-r
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
                        """
                        Não precisamos fazer nada, apenas esperar o temporizador terminar.
                        Uma vez que o temporizador termine e o ACK ainda não tenha sido recebido,
                        o próprio temporizador ficará encarregado de re-enviar o pacote
                        """
                        continue

                    self.sequence_number = (received_seq_num + 1) % 2

                    if self.timer is not None:
                        self.timer.cancel()  # Para o temporizador

                    break

            pause_event.set()

            self.message_serializer.remove_file(self.messages_file_name)

            if message == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.stop()
                break

    def start_timer(self):
        if self.timer is not None:
            self.timer.cancel()

        self.timer_thread = threading.Timer(self.timeout, self.timer_expired)
        self.timer_thread.start()

    def timer_expired(self):
        self.retransmit_packet()

    def retransmit_packet(self):
        # Usando o lock para garantir que a thread vai ter acesso às informações
        with self.lock:
            if self.current_packet:
                decoded_current_packet = json.loads(self.current_packet)

                is_packet_delayed = (
                    self.sequence_number == decoded_current_packet["seq_num"]
                )

                if is_packet_delayed:
                    self.socket.sendto(self.current_packet, self.server_address)
                    self.start_timer()

    def stop(self) -> None:
        print("[CLIENT] Closing socket connection")
        if self.timer is not None:
            self.timer.cancel()
        self.socket.close()

    def listen(self, pause_event: threading.Event) -> None:
        while True:
            if pause_event.is_set():
                try:
                    packet = self.socket.recv(MESSAGE_CHUNK_SIZE_WITH_HEADERS)

                    received_packet = json.loads(packet.decode())

                    message: str = received_packet.get("message")
                    time: str = received_packet.get("time")
                    sender_info: str = received_packet.get("sender_info")

                    if (
                        message == USER_CONNECTED_SUCCESSFULLY_MESSAGE
                        or USER_JOINED_THE_ROOM_MESSAGE in message
                        or USER_LEFT_THE_ROOM_MESSAGE in message
                    ):
                        print(f"\n{message}\n")
                    else:
                        print(f"\n{sender_info}: {message} {time}\n")
                except BlockingIOError:
                    """
                    Ver explicação da linha 76 para mais detalhes
                    """
                    continue
                except OSError:
                    """
                    Isso não deveria acontecer, mas, como estamos lidando com threads,
                    é melhor prevenir do que remediar
                    """
                    continue
