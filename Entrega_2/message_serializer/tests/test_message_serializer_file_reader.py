from message_serializer.serializer import MessageSerializer


DUMMY_FILE_PATH = "message_serializer/tests/fixtures/dummy-file.txt"
DUMMY_FILE_CONTENT = """ESSA É APENAS UMA MENSAGEM DE EXEMPLO, ESTAMOS UTILIZANDO UTF-8 E AFINS.

AGORA TIVEMOS UMA QUEBRA DE LINHA E UM  TAB.

MAIS QUEBRAS DE LINHA E O FINAL DA MENSAGEM.
"""


class TestMessageSerializerFileReader:
    def test_returns_all_content_from_file(self):
        message_serializer = MessageSerializer()

        content = message_serializer.read_all_content_from_file(
            file_path=DUMMY_FILE_PATH
        )

        assert content == DUMMY_FILE_CONTENT
