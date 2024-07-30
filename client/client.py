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
from checksum.checksum import *
import json
import base64
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
        self.timeout = 1  #Timeout em segundos
        self.timer = None  # Temporizador
        self.start_time = None

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
                """
                Dois numeros de sequencia sao usados, um para envio da mensagem e outro para o fim da mensagem
                pois isso sempre será enviado 0 e 1 sucessivamente
                """
                with self.lock:
                    checksum = append_checksum(END_OF_MESSAGE_IDENTIFIER.encode())
                    seq_num = self.sequence_number
                    data = {"message_with_checksum": base64.b64encode(checksum).decode(), "seq_num": seq_num}
                    encoded_data = json.dumps(data).encode()
                    self.socket.sendto(encoded_data, self.server_address)
                    #print(f"mandando pacote com numero de sequencia: {self.sequence_number}")


            self.message_serializer.remove_file(self.messages_file_name)

            if message == CLOSE_CLIENT_SOCKET_MESSAGE:
                self.stop()
                break

    def send_with_sequence(self, chunk):  # Método para enviar a mensagem com o número de sequência
        with self.lock:
            checksum = append_checksum(chunk.encode())
            # Adiciona o checksum ao pacote
            seq_num = self.sequence_number
            self.start_time = time.perf_counter()  #Inicia a contagem do tempo
            data = {"message_with_checksum": base64.b64encode(checksum).decode(), "seq_num": seq_num}
            encoded_data = json.dumps(data).encode()
            self.socket.sendto(encoded_data, self.server_address)
            self.start_timer()  #Inicia o temporizador
            #print(f"mandando pacote com numero de sequencia: {self.sequence_number}")

    def start_timer(self):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.timer_expired)
        self.timer.start()
        #print(f"temporizador iniciado para o numero de sequencia: {self.sequence_number}")

    def timer_expired(self):
        print(f"temporizador expirado para o numero de sequencia:{self.sequence_number}")

    def stop(self) -> None:
        print("[CLIENT] Closing socket connection")
        if self.timer is not None:
            self.timer.cancel()
        self.socket.close()

    def listen(self) -> None:
        while True:
            try:
                received_message, _ = self.socket.recvfrom(MESSAGE_CHUNK_SIZE)
                message = received_message.decode()
                
                if message.startswith(ACK_MESSAGE):
                    ack_number = int(message[len(ACK_MESSAGE):])
                    with self.lock:  #serve pra garantir que o acesso ao dicionário self.acks_received seja seguro, vi em algum fórum
                        self.acks_received[ack_number] = True  #Marca o número de sequência ack_number como "recebido" no dicionario
                        if ack_number == self.sequence_number:
                            #print(f"ack {ack_number} recebido")
                            if self.timer is not None:
                                self.timer.cancel()  # Para o temporizador
                                elapsed_time = time.perf_counter() - self.start_time
                                #print(f"encerrando timer para o numero de sequencia: {ack_number}")
                                #print(f"tempo: {elapsed_time:.6f} seconds")
                            self.sequence_number = 1 - self.sequence_number  # Protocolo bit alternante como no livro, os numeros de sequência são apenas 0 e 1 no RDT3.0

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

'''
Pelo menos até o momento, as linhas 63, 70, 92, 96 e 97 (pode ser que as alterações futuras 
desça as linhas de codigo) tem prints que mostram
a ordem de saída e entrada de cada pacote, e o tempo que cada pacote
leva para ser enviado e recebido.
'''


'''Como não esta implementado o reenvio do pacote, o temporizador expira e o pacote ainda chega ao servidor
é preciso mudar essa logica
'''