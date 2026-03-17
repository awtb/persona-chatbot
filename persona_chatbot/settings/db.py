from persona_chatbot.settings.common import CommonSettings
from persona_chatbot.settings.common import get_env_file


class DatabaseSettings(CommonSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_driver: str = "postgresql+asyncpg"
    db_sync_driver: str = "postgresql+psycopg2"


def get_database_settings(
    env_file: str | None = None,
) -> DatabaseSettings:
    return DatabaseSettings(
        _env_file=get_env_file(env_file),
    )  # type: ignore[call-arg]
