from pydantic import AliasChoices
from pydantic import Field

from persona_chatbot.settings.common import get_env_file
from persona_chatbot.settings.common import RuntimeSettings


class WorkerSettings(RuntimeSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_driver: str = "postgresql+asyncpg"
    db_sync_driver: str = "postgresql+psycopg2"

    worker_host: str = "0.0.0.0"
    worker_port: int = 8001
    worker_processes_count: int = 1

    tg_bot_token: str
    llm_provider_api_key: str = Field(
        default="ollama",
        validation_alias=AliasChoices(
            "LLM_PROVIDER_API_KEY",
            "LLM_API_KEY",
        ),
    )
    llm_provider_base_url: str = Field(
        default="http://localhost:11434/v1",
        validation_alias=AliasChoices(
            "LLM_PROVIDER_BASE_URL",
            "LLM_BASE_URL",
        ),
    )
    llm_model: str = "llama3.2"
    llm_timeout_sec: int = 25
    llm_max_previous_messages: int = 20

    @property
    def host(self) -> str:
        return self.worker_host

    @property
    def port(self) -> int:
        return self.worker_port

    @property
    def processes_count(self) -> int:
        return self.worker_processes_count


def get_worker_settings(env_file: str | None = None) -> WorkerSettings:
    return WorkerSettings(
        _env_file=get_env_file(env_file),
    )  # type: ignore[call-arg]
