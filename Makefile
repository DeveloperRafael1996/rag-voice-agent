.PHONY: help install run dev token clean reset-index lint fix

PYTHON := uv run python
AGENT  := voice_agent.py

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  install      Create venv and install dependencies"
	@echo "  run          Start the voice agent (production mode)"
	@echo "  dev          Start the voice agent in dev/watch mode"
	@echo "  token        Generate a LiveKit access token"
	@echo "  reset-index  Delete persisted vector index (forces rebuild on next run)"
	@echo "  clean        Remove venv and cached files"
	@echo "  lint         Run ruff linter"
	@echo "  fix          Auto-fix ruff lint errors"

install:
	uv sync

run:
	$(PYTHON) $(AGENT) start

dev:
	$(PYTHON) $(AGENT) dev

token:
	$(PYTHON) generation.py

reset-index:
	rm -rf chat-engine-storage/
	@echo "Index cleared — it will be rebuilt on next run."

clean:
	rm -rf .venv __pycache__ **/__pycache__ *.pyc

lint:
	uvx ruff check .

fix:
	uvx ruff check --fix .
