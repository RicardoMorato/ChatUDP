import os
import pytest

from message_serializer.serializer import MessageSerializer

DUMMY_FILE_NAME = "dummy-file.txt"
DUMMY_FILE_CONTENT = "dummy-content"


class TestSerializerFileRemover:
    @pytest.fixture(autouse=True)
    def handle_dummy_file_life_cycle(self):
        # Creates dummy file for test purposes
        file_path = f"message_serializer/files/{DUMMY_FILE_NAME}"

        with open(file_path, "w") as file:
            file.write(DUMMY_FILE_CONTENT)

        yield

        # Removes file after test is done
        if os.path.isfile(file_path):
            os.remove(file_path)

    @pytest.fixture
    def os_remove_mock(self, mocker):
        return mocker.patch("os.remove")

    @pytest.fixture
    def os_is_file_mock(self, mocker):
        return mocker.patch("os.path.isfile")

    def test_removes_file_with_correct_file_path(self, os_is_file_mock, os_remove_mock):
        message_serializer = MessageSerializer()
        message_serializer.remove_file(file_name=DUMMY_FILE_NAME)

        os_is_file_mock.assert_called_once()
        os_remove_mock.assert_called_once_with(
            f"message_serializer/files/{DUMMY_FILE_NAME}"
        )
