import structlog
from faststream import Depends
from faststream.redis import RedisRouter

from persona_chatbot.schemas import ExtractMemoryFactsTaskSchema
from persona_chatbot.services.memory import MemoryService
from persona_chatbot.settings import WorkerSettings
from persona_chatbot.worker.dependencies import get_memory_service
from persona_chatbot.worker.queues import EXTRACT_MEMORY_FACTS_QUEUE

logger = structlog.get_logger(__name__)


def build_router(
    settings: WorkerSettings,
) -> RedisRouter:
    router = RedisRouter()

    @router.subscriber(
        list=EXTRACT_MEMORY_FACTS_QUEUE,
        max_workers=settings.memory_extract_max_workers,
    )
    async def extract_memory_facts(
        payload: ExtractMemoryFactsTaskSchema,
        memory_service: MemoryService = Depends(get_memory_service),
    ) -> None:
        logger.info(
            "Processing memory fact extraction task",
            chat_id=payload.chat_id,
            user_message_id=payload.user_message_id,
            assistant_message_id=payload.assistant_message_id,
            user_message_chars=len(payload.user_message_text),
            assistant_message_chars=len(payload.assistant_message_text),
        )
        await memory_service.extract_facts(
            chat_id=payload.chat_id,
            user_message_id=payload.user_message_id,
            assistant_message_id=payload.assistant_message_id,
            user_message_text=payload.user_message_text,
            assistant_message_text=payload.assistant_message_text,
        )

    return router
