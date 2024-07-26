import threading
import sys
import os
import time
from socket import *

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
    ACK_MESSAGE
)
from message_serializer.serializer import MessageSerializer

class Client:
    def __init__(self, server_port: int, server_host: str = "localhost") -> None:
        self.server_address = (server_host, server_port)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        host, port = self.socket.getsockname()
        self.messages_file_name = f"{host}-{port}"
        self.messages_receiver_file_name = f"{self.messages_file_name}-receiver"
        self.message_serializer = MessageSerializer(chunk_size=MESSAGE_CHUNK_SIZE)
        self.sequence_number = 0
        self.lock = threading.Lock()
        self.acks_received = {}  #ACKs recebidos
        self.timeout = 2  #Timeout em segundos

    def start(self) -> None:
        thread = threading.Thread(daemon=True, target=self.listen)
        thread.start()

        while True:
            message = input("")
            file_path = self.message_serializer.build_messages_file(file_name=self.messages_file_name, message=message)
            chunked_message = self.message_serializer.parse_file_into_message_stream(file_path)

            for chunk in chunked_message:
                self.send_with_sequence(chunk)

            if not GREETING_MESSAGE in message:
                self.socket.sendto(END_OF_MESSAGE_IDENTIFIER.encode(), self.server_address)

            self.message_serializer.remove_file(self.messages_file_name)

            if message == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.stop()
                break

    def send_with_sequence(self, chunk): #Método para enviar a mensagem com o número de sequência
        with self.lock:
            message_with_seq = f"SEQ{self.sequence_number}:{chunk}"
            self.socket.sendto(message_with_seq.encode(), self.server_address)
            self.sequence_number = 1 - self.sequence_number # Protocolo bit alternante como no livro, os numeros de sequência são apenas 0 e 1 no RDT3.0
            #print(self.sequence_number)

    def stop(self) -> None:
        print("[CLIENT] Closing socket connection")
        self.socket.close()

    def listen(self) -> None:
        while True:
            try:
                received_message, _ = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)
                message = received_message.decode()
                
                if message.startswith(ACK_MESSAGE):
                    #print(f"{message}")
                    ack_number = int(message[len(ACK_MESSAGE):])
                    with self.lock: #serve pra garantir que o acesso ao dicionário self.acks_received seja seguro, vi em algum fórum
                        self.acks_received[ack_number] = True #Marca o número de sequência ack_number como "recebido" no dicionário
                
                elif (
                    message == USER_CONNECTED_SUCCESSFULLY_MESSAGE
                    or USER_JOINED_THE_ROOM_MESSAGE in message
                    or USER_LEFT_THE_ROOM_MESSAGE in message
                ):
                    print(f"\n{message}")
                
                else:
                    message_text, host, timestamp = (
                        self.message_serializer.extract_parts_of_received_message(message)
                    )
                    if message_text != END_OF_MESSAGE_IDENTIFIER:
                        file_path = self.message_serializer.build_messages_file(
                            file_name=self.messages_receiver_file_name,
                            message=message_text,
                        )
                    else:
                        text = self.message_serializer.read_all_content_from_file(file_path)
                        print(f"\n{host}: {text} {timestamp}")
                        self.message_serializer.remove_file(self.messages_receiver_file_name)
            
            except error:
                ###ACREDITO QUE AQUI ENTRA O REENVIO DO PACOTE DEPOIS DA IMPLEMENTAÇÃO E VERIFICAÇÃO DO CHECKSUM CASO CONTER ERROS
                print("[CLIENT] Erro ao receber mensagem")

