from faststream.redis import RedisRouter

from persona_chatbot.worker.tasks.memory import router as memory_router
from persona_chatbot.worker.tasks.telegram import router as telegram_router

router = RedisRouter()
router.include_router(telegram_router)
router.include_router(memory_router)

__all__ = ["router"]
