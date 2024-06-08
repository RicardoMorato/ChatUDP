from message_serializer.serializer import MessageSerializer

DUMMY_FILE_PATH = "message_serializer/tests/fixtures/dummy-file.txt"
DUMMY_FILE_CONTENT = """ESSA É APENAS UMA MENSAGEM DE EXEMPLO, ESTAMOS UTILIZANDO UTF-8 E AFINS.

AGORA TIVEMOS UMA QUEBRA DE LINHA E UM  TAB.

MAIS QUEBRAS DE LINHA E O FINAL DA MENSAGEM.
"""
DUMMY_FILE_CONTENT_CHUNK_SIZE_10 = [
    "ESSA É AP",
    "ENAS UMA M",
    "ENSAGEM DE",
    " EXEMPLO, ",
    "ESTAMOS UT",
    "ILIZANDO U",
    "TF-8 E AFI",
    "NS.\n\nAGORA",
    " TIVEMOS U",
    "MA QUEBRA ",
    "DE LINHA E",
    " UM  TAB.\n",
    "\nMAIS QUEB",
    "RAS DE LIN",
    "HA E O FIN",
    "AL DA MENS",
    "AGEM.\n",
]


class TestSerializerFileParser:
    def test_returns_content_from_file(self):
        message_serializer = MessageSerializer()

        content = list(
            message_serializer.parse_file_into_message_stream(file_path=DUMMY_FILE_PATH)
        )[0]

        assert content is not None
        assert content == DUMMY_FILE_CONTENT

    def test_returns_content_respecting_chunk_size(self):
        chunk_size = 10

        message_serializer = MessageSerializer(chunk_size=chunk_size)

        chunks = message_serializer.parse_file_into_message_stream(
            file_path=DUMMY_FILE_PATH
        )

        for index, chunk in enumerate(chunks):
            # Verifica se os chunks realmente trazem o output esperado
            assert chunk == DUMMY_FILE_CONTENT_CHUNK_SIZE_10[index]

            # Verifica se todos os chunks respeitam o threshold
            assert len(chunk) <= chunk_size
