import os

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class CommonSettings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    logging_mode: str = "plain"
    logging_lvl: str = "INFO"
    service_name: str = "persona-chatbot"

    model_config = SettingsConfigDict(
        extra="ignore", env_ignore_empty=True, env_file=".env"
    )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class RuntimeSettings(CommonSettings):
    @property
    def host(self) -> str:
        raise NotImplementedError

    @property
    def port(self) -> int:
        raise NotImplementedError

    @property
    def processes_count(self) -> int:
        raise NotImplementedError


def get_env_file(env_file: str | None) -> str:
    if env_file is not None:
        return env_file

    return os.getenv("SETTINGS_ENV_FILE", ".env")
