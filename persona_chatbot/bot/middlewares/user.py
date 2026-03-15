from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.db.repos.user import UserRepo
from persona_chatbot.services.user import UserService


class UserDependenciesMiddleware(BaseMiddleware):
    @staticmethod
    def _require_session(
        data: dict[str, Any],
    ) -> AsyncSession:
        session = data.get("session")
        if not isinstance(session, AsyncSession):
            msg = (
                "UserDependenciesMiddleware requires AsyncSession in context. "
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

        data["user_repo"] = UserRepo(session=session)
        data["user_service"] = UserService(session=session)

        return await handler(event, data)


class CurrentUserProviderMiddleware(BaseMiddleware):
    @staticmethod
    def _require_telegram_user(
        data: dict[str, Any],
    ) -> TelegramUser:
        tg_user = data.get("event_from_user")
        if not isinstance(tg_user, TelegramUser):
            msg = "CurrentUserProviderMiddleware requires Telegram user."
            raise RuntimeError(msg)

        return tg_user

    @staticmethod
    def _require_user_service(
        data: dict[str, Any],
    ) -> UserService:
        user_service = data.get("user_service")
        if not isinstance(user_service, UserService):
            msg = (
                "CurrentUserProviderMiddleware requires "
                "UserService in context. "
                "Ensure UserDependenciesMiddleware is registered before it."
            )
            raise RuntimeError(msg)

        return user_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_service = self._require_user_service(data=data)
        tg_user = self._require_telegram_user(data=data)
        data["current_user"] = await user_service.get_or_create(
            telegram_user_id=tg_user.id,
        )

        return await handler(event, data)
