import structlog
from faststream import Context
from faststream.redis import RedisRouter
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.memory import MemoryFactRepo
from persona_chatbot.db.repos.message import MessageRepo
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.schemas import ExtractMemoryFactsTaskSchema
from persona_chatbot.services.memory import MemoryService
from persona_chatbot.worker.lifecycle import LLM_CLIENT_CONTEXT_KEY
from persona_chatbot.worker.lifecycle import SESSION_MAKER_CONTEXT_KEY
from persona_chatbot.worker.queues import EXTRACT_MEMORY_FACTS_QUEUE

logger = structlog.get_logger(__name__)
router = RedisRouter()


@router.subscriber(list=EXTRACT_MEMORY_FACTS_QUEUE)
async def extract_memory_facts(
    payload: ExtractMemoryFactsTaskSchema,
    session_maker: async_sessionmaker[AsyncSession] = Context(
        SESSION_MAKER_CONTEXT_KEY
    ),
    llm_client: LLMClient = Context(LLM_CLIENT_CONTEXT_KEY),
) -> None:
    logger.info(
        "Processing memory fact extraction task",
        chat_id=payload.chat_id,
    )
    async with session_maker() as session:
        try:
            memory_service = MemoryService(
                chat_repo=ChatRepo(session=session),
                message_repo=MessageRepo(session=session),
                memory_fact_repo=MemoryFactRepo(session=session),
                llm_client=llm_client,
            )
            await memory_service.extract_facts(chat_id=payload.chat_id)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
