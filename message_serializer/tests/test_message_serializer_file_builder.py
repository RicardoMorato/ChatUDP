from message_serializer.serializer import MessageSerializer

DUMMY_FILE_NAME = "dummy-file.txt"


class TestSerializerFileBuilder:
    def test_creates_file_with_correct_file_path(self, mocker):
        open_mock = mocker.patch("builtins.open")

        message_serializer = MessageSerializer()
        message_serializer.build_messages_file(file_name=DUMMY_FILE_NAME)

        open_mock.assert_called_once_with(
            f"message_serializer/files/{DUMMY_FILE_NAME}", "a"
        )

