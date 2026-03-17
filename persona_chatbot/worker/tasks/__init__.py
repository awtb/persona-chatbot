from faststream.redis import RedisRouter

from persona_chatbot.settings import WorkerSettings
from persona_chatbot.worker.tasks.memory import router as memory_router
from persona_chatbot.worker.tasks.telegram import (
    build_router as build_telegram_router,
)


def build_router(
    settings: WorkerSettings,
) -> RedisRouter:
    router = RedisRouter()
    router.include_router(
        build_telegram_router(settings=settings),
    )
    router.include_router(memory_router)
    return router


__all__ = ["build_router"]
