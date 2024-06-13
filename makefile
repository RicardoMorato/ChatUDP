.PHONY: test client server

test:
	PYTHONPATH=. pytest

client:
	python -m client.client

server:
	python -m server.server