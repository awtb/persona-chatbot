from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from faststream.redis import RedisBroker
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.memory import MemoryFactRepo
from persona_chatbot.db.repos.message import MessageRepo
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.services.avatar import AvatarService
from persona_chatbot.services.chat import ChatService
from persona_chatbot.settings import WorkerSettings


class ChatDependenciesMiddleware(BaseMiddleware):
    def __init__(
        self,
        broker: RedisBroker,
    ) -> None:
        self._broker = broker
        self._llm_client: LLMClient | None = None

    @staticmethod
    def _require_settings(
        data: dict[str, Any],
    ) -> WorkerSettings:
        settings = data.get("settings")
        if not isinstance(settings, WorkerSettings):
            msg = (
                "ChatDependenciesMiddleware requires "
                "WorkerSettings in context. Ensure "
                "SettingsProviderMiddleware is registered "
                "before it."
            )
            raise RuntimeError(msg)

        return settings

    @staticmethod
    def _require_session(
        data: dict[str, Any],
    ) -> AsyncSession:
        session = data.get("session")
        if not isinstance(session, AsyncSession):
            msg = (
                "ChatDependenciesMiddleware requires AsyncSession in context. "
                "Ensure SessionProviderMiddleware is registered before it."
            )
            raise RuntimeError(msg)

        return session

    @staticmethod
    def _require_avatar_service(
        data: dict[str, Any],
    ) -> AvatarService:
        avatar_service = data.get("avatar_service")
        if not isinstance(avatar_service, AvatarService):
            msg = (
                "ChatDependenciesMiddleware requires "
                "AvatarService in context. "
                "Ensure AvatarDependenciesMiddleware is registered before it."
            )
            raise RuntimeError(msg)

        return avatar_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        settings = self._require_settings(data=data)
        if self._llm_client is None:
            self._llm_client = LLMClient(
                api_key=settings.llm_provider_api_key,
                base_url=settings.llm_provider_base_url,
                model=settings.llm_model,
                timeout_sec=settings.llm_timeout_sec,
            )
        session = self._require_session(data=data)
        avatar_service = self._require_avatar_service(data=data)

        data["chat_service"] = ChatService(
            llm_client=self._llm_client,
            avatar_service=avatar_service,
            chat_repo=ChatRepo(session=session),
            message_repo=MessageRepo(session=session),
            memory_fact_repo=MemoryFactRepo(session=session),
            broker=self._broker,
            max_previous_messages=settings.llm_max_previous_messages,
        )
        return await handler(event, data)
