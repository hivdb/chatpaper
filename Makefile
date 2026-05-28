init:
	@uv sync

sync:
	@uv sync

lock:
	@uv lock

# check-ai-memory:
# 	@uv run python check_ai_memory/work.py

chat:
	@uv run python work.py

dump-encoding:
	@uv run python -c 'import tiktoken; tiktoken.get_encoding("cl100k_base")'

ipython:
	@uv run ipython

.PHONY: init sync lock check-ai-memory chat dump-encoding ipython
