.PHONY: help install install-openai run run-openai dev dev-openai token clean reset-index lint fix

PYTHON     := uv run python
PYTHON_OAI := .venv/bin/python
AGENT      := voice_agent.py
AGENT_OAI  := voice_agent_openai.py

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  install        Create venv and install dependencies"
	@echo "  install-openai Install extra deps for OpenAI agent"
	@echo "  run            Start the voice agent with Ollama (local)"
	@echo "  run-openai     Start the voice agent with OpenAI"
	@echo "  dev            Dev/watch mode with Ollama"
	@echo "  dev-openai     Dev/watch mode with OpenAI"
	@echo "  token          Generate a LiveKit access token"
	@echo "  reset-index    Delete persisted vector index (forces rebuild on next run)"
	@echo "  clean          Remove venv and cached files"
	@echo "  lint           Run ruff linter"
	@echo "  fix            Auto-fix ruff lint errors"

install:
	uv sync

install-openai:
	uv sync
	uv pip install --no-deps "llama-index-llms-openai==0.8.3"
	uv pip install "openai>=3.19,<4"

run:
	$(PYTHON) $(AGENT) start

run-openai:
	$(PYTHON_OAI) $(AGENT_OAI) start

dev:
	$(PYTHON) $(AGENT) dev

dev-openai:
	$(PYTHON_OAI) $(AGENT_OAI) dev

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
