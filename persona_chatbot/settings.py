import os

from pydantic import AliasChoices
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_driver: str = "postgresql+asyncpg"
    db_sync_driver: str = "postgresql+psycopg2"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_username: str | None = None
    redis_password: str | None = None

    serving_host: str = "0.0.0.0"
    serving_port: int = 8000
    serving_workers_count: int = 1

    tg_bot_token: str
    tg_bot_webhook_url: str
    tg_bot_webhook_token: str
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

    logging_mode: str = "plain"
    logging_lvl: str = "INFO"
    service_name: str = "persona-chatbot"

    cors_allow_origins: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_credentials: bool = True

    model_config = SettingsConfigDict(
        extra="ignore", env_ignore_empty=True, env_file=".env"
    )


def get_settings(env_file: str | None = None) -> Settings:
    target_env_file = env_file or os.getenv("SETTINGS_ENV_FILE", ".env")
    return Settings(_env_file=target_env_file)  # type: ignore[call-arg]
