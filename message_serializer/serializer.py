import os

from typing import Optional, Generator

from common.constants import MESSAGE_CHUNK_SIZE


class MessageSerializer:
    def __init__(self, chunk_size: Optional[int] = MESSAGE_CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size
        self.files_dir = "message_serializer/files/"

    def parse_file_into_message_stream(self, file_path: str = "") -> Generator:
        with open(file_path, "rb") as file:
            while True:
                content = file.read(self.chunk_size)

                if not content:
                    break

                text = content.decode(encoding="utf-8")

                yield text

    def read_all_content_from_file(self, file_path: str = "") -> str:
        text = ""

        with open(file_path, "r") as file:
            while True:
                content = file.read()

                if not content:
                    break

                text = text.join(content)

        return text

    def build_messages_file(
        self, file_name: str = "", message: Optional[str] = None
    ) -> str:
        file_path = os.path.join(self.files_dir, file_name)

        with open(file_path, "a") as file:
            file.write(message)

        return file_path

    def remove_file(self, file_name: str = "") -> None:
        file_path = os.path.join(self.files_dir, file_name)

        if os.path.isfile(file_path):
            os.remove(file_path)
