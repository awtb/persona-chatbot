.PHONY: install migrate dev prod pre-commit test

PYRUN = PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" uv run python -m
APP = $(PYRUN) persona_chatbot

install:
	uv venv .venv
	uv sync --frozen
	uv run pre-commit install

migrate:
	uv run alembic upgrade head

dev: migrate
	$(APP) --reload

prod: migrate
	LOGGING_MODE=structured $(APP)

pre-commit:
	uv run pre-commit run --all-files
