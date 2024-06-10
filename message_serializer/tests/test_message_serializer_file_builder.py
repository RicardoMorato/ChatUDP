import os
import pytest

from message_serializer.serializer import MessageSerializer

DUMMY_FILE_NAME = "dummy-file.txt"


class TestSerializerFileBuilder:
    @pytest.fixture(autouse=True)
    def remove_dummy_file(self):
        yield
        file_path = f"message_serializer/files/{DUMMY_FILE_NAME}"

        if os.path.isfile(file_path):
            os.remove(file_path)

    def test_creates_file_with_correct_file_path(self, mocker):
        open_mock = mocker.patch("builtins.open")

        message_serializer = MessageSerializer()
        message_serializer.build_messages_file(file_name=DUMMY_FILE_NAME)

        open_mock.assert_called_once_with(
            f"message_serializer/files/{DUMMY_FILE_NAME}", "a"
        )

    def test_adds_message_to_file(self):
        example_message = "MENSAGEM DE EXEMPLO"

        message_serializer = MessageSerializer()
        file_path = message_serializer.build_messages_file(
            file_name=DUMMY_FILE_NAME, message=example_message
        )

        assert file_path is not None

        with open(file_path, "r", encoding="utf-8") as test_file:
            content = test_file.read()

            assert content == example_message

    def test_adds_multiple_messages_to_same_file(self):
        example_messages = [
            "THIS",
            " IS",
            " AN",
            " EXAMPLE",
            " OF",
            " MESSAGE",
            " STREAMS",
        ]

        # expected_output will read as "THIS IS AN EXAMPLE OF MESSAGE STREAMS"
        expected_output = "".join(example_messages)

        message_serializer = MessageSerializer()

        for message in example_messages:
            file_path = message_serializer.build_messages_file(
                file_name=DUMMY_FILE_NAME, message=message
            )

        assert file_path is not None

        with open(file_path, "r", encoding="utf-8") as test_file:
            content = test_file.read()

            assert content == expected_output
