SHELL := /bin/sh

.PHONY: install migrate api-dev api-prod worker-dev worker-prod dev prod pre-commit

UV = uv
UV_RUN = $(UV) run
APP = PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" $(UV_RUN) python -m persona_chatbot
START = $(APP)
API_DEV = $(START) api --reload
WORKER_DEV = $(START) worker --reload
API_PROD = LOGGING_MODE=structured $(START) api
WORKER_PROD = LOGGING_MODE=structured $(START) worker

install:
	$(UV) venv .venv
	$(UV) sync --frozen
	$(UV_RUN) pre-commit install

migrate:
	$(UV_RUN) alembic upgrade head

api-dev: migrate
	$(API_DEV)

api-prod: migrate
	$(API_PROD)

worker-dev: migrate
	$(WORKER_DEV)

worker-prod: migrate
	$(WORKER_PROD)

dev: migrate
	sh -c 'trap "kill 0" INT TERM EXIT; $(WORKER_DEV) & $(API_DEV)'

prod: migrate
	sh -c 'trap "kill 0" INT TERM EXIT; $(WORKER_PROD) & $(API_PROD)'

pre-commit:
	$(UV_RUN) pre-commit run --all-files
