import os
import re

from typing import Optional, Generator, Tuple

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

    def extract_parts_of_received_message(self, received_message: str) -> Tuple[str]:
        """
        Esse método recebe uma mensagem no padrão `~host: mensagem 12:34:56 01/01/2022` (i.e. `~<HOST>: <MESSAGE> <TIMESTAMP>`)
        e retorna um tripla no formato (message, host, timestamp).

        O método utiliza padrões RegExp para extrair cada uma dessas partes da mensagem.
        Caso não seja possível extrair as partes da mensagem, uma exceção será lançada.

        Os padrões utilizados são:

        ```python
        r"~[^:]+: (.+?) \d{2}:\d{2}:\d{2} \d{2}/\d{2}/\d{4}"
        ```

        Para capturar apenas a mensagem.

        E o padrão

        ```python
        r"^(.*?): .+? (\d{2}:\d{2}:\d{2} \d{2}/\d{2}/\d{4})$"
        ```

        Para capturar o host e o timestamp da mensagem.

        Para mais informações e exemplos de como utilizar RegExp, os sites [RegexOne](https://regexone.com/) e [Regex101](https://regex101.com/)
        são ótimos materiais de estudo.

        Para exemplos de utilização do método, o arquivo de testes desse método
        ([test_message_serializer_message_extractor.py](message_serializer/tests/test_message_serializer_message_extractor.py))
        traz alguns casos de uso interessantes.
        """

        extract_message_text_pattern = (
            r"~[^:]+: (.+?) \d{2}:\d{2}:\d{2} \d{2}/\d{2}/\d{4}"
        )

        extract_host_and_timestamp_pattern = (
            r"^(.*?): .+? (\d{2}:\d{2}:\d{2} \d{2}/\d{2}/\d{4})$"
        )

        regexp_match = re.search(extract_message_text_pattern, received_message)

        if regexp_match:
            message = regexp_match.group(1)

        regexp_match = re.search(extract_host_and_timestamp_pattern, received_message)

        if regexp_match:
            host = regexp_match.group(1)
            timestamp = regexp_match.group(2)

        return message, host, timestamp
