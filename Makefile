init:
	@python -m venv env
	@./env/bin/pip3 install -r requirements.txt

freeze:
	@./env/bin/pip3 freeze > requirements.txt

# check-ai-memory:
# 	@./env/bin/python check_ai_memory/work.py

chat:
	@./env/bin/python work.py

dump-encoding:
	@./env/bin/python -c 'import tiktoken; tiktoken.get_encoding("cl100k_base")'

ipython:
	@./env/bin/ipython

.PHONY: init freeze check-ai-memory chat dump-encoding ipython
