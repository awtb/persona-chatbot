from persona_chatbot.settings.common import get_env_file
from persona_chatbot.settings.common import RuntimeSettings


class ApiSettings(RuntimeSettings):
    serving_host: str = "0.0.0.0"
    serving_port: int = 8000
    serving_processes_count: int = 1

    tg_bot_token: str
    tg_bot_webhook_url: str
    tg_bot_webhook_token: str

    cors_allow_origins: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_credentials: bool = True

    @property
    def host(self) -> str:
        return self.serving_host

    @property
    def port(self) -> int:
        return self.serving_port

    @property
    def processes_count(self) -> int:
        return self.serving_processes_count


def get_api_settings(env_file: str | None = None) -> ApiSettings:
    return ApiSettings(
        _env_file=get_env_file(env_file),
    )  # type: ignore[call-arg]
