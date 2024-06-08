from typing import Optional
from message_serializer.constants import CHUNK_SIZE


class MessageSerializer:
    def __init__(self, chunk_size: Optional[int] = CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size

    def parse_file_into_message_stream(self, file_path: str = ""):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            return content
