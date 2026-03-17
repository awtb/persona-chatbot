from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from faststream.redis import RedisBroker

from persona_chatbot.api.dependencies.common import get_settings
from persona_chatbot.settings import ApiSettings


def validate_tg_webhook_token(
    secret_token: str = Header(
        validation_alias="X-Telegram-Bot-Api-Secret-Token",
    ),
    settings: ApiSettings = Depends(get_settings),
) -> None:
    if settings.tg_bot_webhook_token != secret_token:
        raise HTTPException(
            detail="Seriously?",
            status_code=status.HTTP_403_FORBIDDEN,
        )


def get_telegram_updates_broker(request: Request) -> RedisBroker:
    return request.app.state.tg_updates_broker
