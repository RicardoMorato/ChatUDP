from message_serializer.serializer import MessageSerializer


class TestSerializerFileParser:
    def test_opens_correct_file_path(self, mocker):
        DUMMY_FILE_PATH = "/dummy-file.txt"
        open_mock = mocker.patch("builtins.open")

        message_serializer = MessageSerializer()

        message_serializer.parse_file_into_message_stream(file_path=DUMMY_FILE_PATH)

        open_mock.assert_called_once_with(DUMMY_FILE_PATH, "r", encoding="utf-8")
