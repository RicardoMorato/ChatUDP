.PHONY: test client server

test:
	PYTHONPATH=. pytest

client:
	python -m client.main

server:
	python -m server.server