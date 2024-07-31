import pytest

from message_serializer.serializer import MessageSerializer


class TestExtractPartsOfReceivedMessage:
    def test_extracts_text_from_received_message(self):
        received_message = "127.0.0.1:64179/~user: olá, tudo bem? 17:32:32 19/06/2024"
        expected_extracted_text = "olá, tudo bem?"

        message_serializer = MessageSerializer()

        message, _, _ = message_serializer.extract_parts_of_received_message(
            received_message
        )

        assert message == expected_extracted_text

    def test_extracts_host_from_received_message(self):
        received_message = "127.0.0.1:64179/~user: olá, tudo bem? 17:32:32 19/06/2024"
        expected_extracted_host = "127.0.0.1:64179/~user"

        message_serializer = MessageSerializer()

        _, host, _ = message_serializer.extract_parts_of_received_message(
            received_message
        )

        assert host == expected_extracted_host

    def test_extracts_timestamp_from_received_message(self):
        received_message = "127.0.0.1:64179/~user: olá, tudo bem? 17:32:32 19/06/2024"
        expected_extracted_timestamp = "17:32:32 19/06/2024"

        message_serializer = MessageSerializer()

        _, _, timestamp = message_serializer.extract_parts_of_received_message(
            received_message
        )

        assert timestamp == expected_extracted_timestamp

    @pytest.mark.parametrize(
        ["received_message", "expected_host", "expected_message", "expected_timestamp"],
        [
            [
                "127.0.0.1:64179/~user: olá, tudo bem? 17:32:32 19/06/2024",
                "127.0.0.1:64179/~user",
                "olá, tudo bem?",
                "17:32:32 19/06/2024",
            ],
            [
                "127.0.0.1:64179/~very-long-user-name-here: olá, tudo bem? 17:32:32 19/06/2024",
                "127.0.0.1:64179/~very-long-user-name-here",
                "olá, tudo bem?",
                "17:32:32 19/06/2024",
            ],
            [
                "127.0.0.1:64179/~user: MENSAGEM TODA EM CAPS E BASTANTE LONGA AA A A A A  A A A A A A A A A A A A A A A A A A  A A A A A A  A A A A A A A A A A A A A A A A  A A A A A A 17:32:32 19/06/2024",
                "127.0.0.1:64179/~user",
                "MENSAGEM TODA EM CAPS E BASTANTE LONGA AA A A A A  A A A A A A A A A A A A A A A A A A  A A A A A A  A A A A A A A A A A A A A A A A  A A A A A A",
                "17:32:32 19/06/2024",
            ],
        ],
    )
    def test_handles_multiple_formatted_messages(
        self, received_message, expected_host, expected_message, expected_timestamp
    ):
        message_serializer = MessageSerializer()

        message, host, timestamp = message_serializer.extract_parts_of_received_message(
            received_message
        )

        assert message == expected_message
        assert host == expected_host
        assert timestamp == expected_timestamp
