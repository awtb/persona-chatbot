from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types import TelegramObject
from redis.asyncio import Redis

CHAT_PROCESSING_LOCK_TTL_SEC = 120
CHAT_PROCESSING_WAIT_TEXT = "You already asked something, please wait."
logger = structlog.get_logger(__name__)


class ChatProcessingMiddleware(BaseMiddleware):
    def __init__(
        self,
        redis: Redis,
    ) -> None:
        self._redis = redis

    @staticmethod
    def _build_lock_key(
        tg_user_id: int,
    ) -> str:
        return f"chat-processing:{tg_user_id}"

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        if event.text is None:
            return await handler(event, data)
        if event.text.startswith("/"):
            return await handler(event, data)
        if event.from_user is None:
            return await handler(event, data)

        logger.info(
            "Attempting chat processing lock",
            telegram_user_id=event.from_user.id,
        )
        lock_key = self._build_lock_key(
            tg_user_id=event.from_user.id,
        )
        lock_acquired = await self._redis.set(
            lock_key,
            "1",
            ex=CHAT_PROCESSING_LOCK_TTL_SEC,
            nx=True,
        )
        if not lock_acquired:
            logger.info(
                "Chat processing lock rejected",
                telegram_user_id=event.from_user.id,
                lock_key=lock_key,
            )
            await event.answer(CHAT_PROCESSING_WAIT_TEXT)
            return None

        logger.info(
            "Chat processing lock acquired",
            telegram_user_id=event.from_user.id,
            lock_key=lock_key,
        )
        try:
            return await handler(event, data)
        finally:
            await self._redis.delete(lock_key)
            logger.info(
                "Chat processing lock released",
                telegram_user_id=event.from_user.id,
                lock_key=lock_key,
            )
