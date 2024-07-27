def bytes_to_bits_binary(byte_data: bytes) -> str:
    #converte os dados de bytes para uma string binária
    bits_data = bin(int.from_bytes(byte_data, byteorder='big'))[2:]
    #preenche com zeros à esquerda para garantir que o comprimento seja múltiplo de 8
    return bits_data.zfill(len(byte_data) * 8)


def find_sum_checksum(message: bytes) -> str:
    #converte a mensagem para uma sequência binária de bits
    message_bits = bytes_to_bits_binary(message)
    slice_length = 8  # Comprimento de cada pacote de bits
    checksum_array = [message_bits[i:i + slice_length] for i in range(0, len(message_bits), slice_length)]
    total_sum = sum(int(binary, 2) for binary in checksum_array)
    sum_binary = bin(total_sum)[2:]
    return sum_binary.zfill(16)


def find_checksum(message: bytes) -> str:
    #calcula a soma binária dos pacotes de bits
    sum_checksum = find_sum_checksum(message)

    #adiciona os bits de overflow (em caso de ter)
    if len(sum_checksum) > 16:
        overflow = len(sum_checksum) - 16
        sum_checksum = bin(int(sum_checksum[:overflow], 2) + int(sum_checksum[overflow:], 2))[2:]

    sum_checksum = sum_checksum.zfill(16)

    #calcular o complemento da soma
    checksum = ''.join('0' if bit == '1' else '1' for bit in sum_checksum)
    return checksum


def verify_checksum(message: bytes, expected_checksum: str) -> bool:
    calculated_checksum = find_checksum(message)
    return calculated_checksum == expected_checksum


def append_checksum(message: bytes) -> bytes:
    checksum = find_checksum(message)
    #converte o checksum binário para bytes
    checksum_bytes = int(checksum, 2).to_bytes(2, byteorder='big')
    return message + checksum_bytes


def extract_data_and_checksum(message_with_checksum: bytes) -> (bytes, str):
    if len(message_with_checksum) < 2:
        raise ValueError("Dados são menores que o comprimento esperado para o checksum.")

    checksum_length = 2  #comprimento do checksum em bytes
    data = message_with_checksum[:-checksum_length]  
    checksum = bin(int.from_bytes(message_with_checksum[-checksum_length:], byteorder='big'))[2:].zfill(
        16)  #checksum extraído
    return data, checksum