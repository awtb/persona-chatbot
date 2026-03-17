# Persona Chatbot 🎭

Telegram bot with selectable AI avatars, streamed replies, short-term chat history, and long-term fact memory.

The project is built around a queue-backed runtime:

- FastAPI accepts Telegram webhooks
- Redis queues raw updates and background jobs
- FastStream worker runs aiogram handlers and background memory extraction
- PostgreSQL stores users, avatars, chats, messages, and memory facts

For the deeper architecture and flow design, see [docs/design.md](docs/design.md).

## Demo

Screenshots demonstrating the bot, including long-term memory recall after chat
reset, are collected in [.github/DEMO.md](.github/DEMO.md).

## Features

- Avatar-based chat personas
- Avatar preview before selection
- Streamed Telegram replies
- Per-user chat locking to avoid overlapping generations
- Recent chat history as short-term memory
- Durable fact extraction as long-term memory
- Facts browser by avatar
- Chat history viewer
- Chat reset without deleting long-term memory
- Docker-first local setup

## Bot Commands

- `/start` - open the welcome flow
- `/menu` - open quick actions
- `/avatars` - choose an avatar
- `/history` - show recent chat messages
- `/facts` - browse stored facts by avatar
- `/reset` - start a fresh chat with the current avatar

The LLM integration expects an OpenAI-compatible API. Ollama is only one
possible backend, not a special built-in mode.

## Included Avatars

- Donald Trump - loud, boastful, combative persona focused on winning, status, and spectacle
- Jeffrey Epstein - cold, manipulative elite-network persona with restrained, ironic tone
- Professor Moriarty - theatrical criminal mastermind persona with polished, hypnotic delivery
- Pavel Durov - calm, minimalist, privacy-focused tech idealist persona

## Disclaimer

All personas and characterizations in this project are fictionalized constructs
created for demonstration purposes. They are not intended to depict any real
person accurately or to make factual claims about any real individual. Any
overlap in names, traits, or references should be understood as part of the
project's fictional framing.

## Quick Start

### Docker

Before starting, make sure Docker and Docker Compose are installed on your
machine.

The bot works through Telegram webhooks only. For local development, you need a
public HTTPS URL that forwards requests to your API. A tunnel such as
[ngrok](https://ngrok.com/) is a valid option.

1. Create an env file from the example:

```bash
cp .env.example .env
```

2. Fill the required values in `.env`:

- `TG_BOT_TOKEN`
- `TG_BOT_WEBHOOK_URL`
- `TG_BOT_WEBHOOK_TOKEN`
- `LLM_PROVIDER_API_KEY`
- `LLM_PROVIDER_BASE_URL`
- `LLM_MODEL`

`TG_BOT_WEBHOOK_URL` must point to the app webhook endpoint, which is served at
`/telegram`.

`TG_BOT_WEBHOOK_TOKEN` is the secret token used to verify that incoming webhook
requests really come from Telegram.

The app expects an OpenAI-compatible API endpoint.

Recommended hosted setup:

```env
LLM_PROVIDER_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
```

If you prefer a local OpenAI-compatible endpoint, the example configuration
uses `http://host.docker.internal:11434/v1`, which works for tools like Ollama
that expose an OpenAI-compatible API.

3. Start the full Docker setup:

```bash
make compose
```

This runs avatar seeding first and then starts the application stack.

If you want to run the Docker steps manually:

```bash
docker compose --profile seed run --rm seed
docker compose up --build
```

### Local development

1. Install dependencies:

```bash
make install
```

2. Run migrations:

```bash
make migrate
```

3. Start API and worker:

```bash
make dev
```

Or run them separately:

```bash
make api-dev
make worker-dev
```

## Observability

The project can emit structured JSON logs via `LOGGING_MODE=structured`. This
format is convenient for log aggregation and analysis in systems such as
VictoriaLogs and Grafana.

Example configuration:

```env
LOGGING_MODE=structured
LOGGING_LVL=INFO
```
