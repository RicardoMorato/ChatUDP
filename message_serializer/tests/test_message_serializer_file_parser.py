import pytest

from message_serializer.serializer import MessageSerializer

DUMMY_FILE_PATH = "message_serializer/tests/fixtures/dummy-file.txt"
DUMMY_FILE_CONTENT = """ESSA É APENAS UMA MENSAGEM DE EXEMPLO, ESTAMOS UTILIZANDO UTF-8 E AFINS.

AGORA TIVEMOS UMA QUEBRA DE LINHA E UM  TAB.

MAIS QUEBRAS DE LINHA E O FINAL DA MENSAGEM.
"""
DUMMY_FILE_FIRST_CHUNK_SIZE_10 = "ESSA É AP"  # O acento agudo toma 1 byte


class TestSerializerFileParser:
    def test_returns_content_from_file(self):
        message_serializer = MessageSerializer()

        content = list(
            message_serializer.parse_file_into_message_stream(file_path=DUMMY_FILE_PATH)
        )[0]

        assert content is not None
        assert content == DUMMY_FILE_CONTENT

    def test_returns_content_respecting_chunk_size(self):
        chunk_size = 10

        message_serializer = MessageSerializer(chunk_size=chunk_size)

        chunks = list(
            message_serializer.parse_file_into_message_stream(file_path=DUMMY_FILE_PATH)
        )

        first_message = chunks[0]
        assert first_message == DUMMY_FILE_FIRST_CHUNK_SIZE_10

        # Verifica se todos os chunks respeitam o threshold
        for chunk in chunks:
            assert len(chunk) <= chunk_size
