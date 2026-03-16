import structlog
from faststream import Depends
from faststream.redis import RedisRouter

from persona_chatbot.schemas import ExtractMemoryFactsTaskSchema
from persona_chatbot.services.memory import MemoryService
from persona_chatbot.worker.dependencies import get_memory_service
from persona_chatbot.worker.queues import EXTRACT_MEMORY_FACTS_QUEUE

logger = structlog.get_logger(__name__)
router = RedisRouter()


@router.subscriber(list=EXTRACT_MEMORY_FACTS_QUEUE)
async def extract_memory_facts(
    payload: ExtractMemoryFactsTaskSchema,
    memory_service: MemoryService = Depends(get_memory_service),
) -> None:
    logger.info(
        "Processing memory fact extraction task",
        chat_id=payload.chat_id,
    )
    await memory_service.extract_facts(chat_id=payload.chat_id)
