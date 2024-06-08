import os
from typing import Optional
from message_serializer.constants import CHUNK_SIZE


class MessageSerializer:
    def __init__(self, chunk_size: Optional[int] = CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size
        self.files_dir = "message_serializer/files/"

    def parse_file_into_message_stream(self, file_path: str = ""):
        with open(file_path, "rb") as file:
            while True:
                content = file.read(self.chunk_size)

                if not content:
                    break

                text = content.decode(encoding="utf-8")

                yield text

    def build_messages_file(self, file_name: str = "", message: Optional[str] = None):
        file_path = os.path.join(self.files_dir, file_name)

        with open(file_path, "a") as file:
            file.write(message)

        return file_path
