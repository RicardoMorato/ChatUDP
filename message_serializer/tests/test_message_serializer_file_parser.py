from message_serializer.serializer import MessageSerializer

DUMMY_FILE_PATH = "message_serializer/tests/fixtures/dummy-file.txt"
DUMMY_FILE_CONTENT = """ESSA É APENAS UMA MENSAGEM DE EXEMPLO, ESTAMOS UTILIZANDO UTF-8 E AFINS.

AGORA TIVEMOS UMA QUEBRA DE LINHA E UM  TAB.

MAIS QUEBRAS DE LINHA E O FINAL DA MENSAGEM.
"""


class TestSerializerFileParser:
    def test_opens_correct_file_path(self, mocker):
        open_mock = mocker.patch("builtins.open")

        message_serializer = MessageSerializer()

        message_serializer.parse_file_into_message_stream(file_path=DUMMY_FILE_PATH)

        open_mock.assert_called_once_with(DUMMY_FILE_PATH, "r", encoding="utf-8")

    def test_returns_content_from_file(self):
        message_serializer = MessageSerializer()

        content = message_serializer.parse_file_into_message_stream(
            file_path=DUMMY_FILE_PATH
        )

        assert content is not None
        assert content == DUMMY_FILE_CONTENT
