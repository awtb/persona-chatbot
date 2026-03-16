from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from persona_chatbot.settings import Settings


class SettingsProviderMiddleware(BaseMiddleware):
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self._settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["settings"] = self._settings
        return await handler(event, data)
