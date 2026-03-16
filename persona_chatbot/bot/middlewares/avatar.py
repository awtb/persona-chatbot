from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.services.avatar import AvatarService


class AvatarDependenciesMiddleware(BaseMiddleware):
    @staticmethod
    def _require_session(
        data: dict[str, Any],
    ) -> AsyncSession:
        session = data.get("session")
        if not isinstance(session, AsyncSession):
            msg = (
                "AvatarDependenciesMiddleware requires "
                "AsyncSession in context. "
                "Ensure SessionProviderMiddleware is registered before it."
            )
            raise RuntimeError(msg)

        return session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session = self._require_session(data=data)
        data["avatar_service"] = AvatarService(session=session)

        return await handler(event, data)
