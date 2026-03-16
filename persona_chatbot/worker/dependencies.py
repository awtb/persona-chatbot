from collections.abc import AsyncIterator

from faststream import Context
from faststream import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.memory import MemoryFactRepo
from persona_chatbot.db.repos.message import MessageRepo
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.services.memory import MemoryService
from persona_chatbot.worker.lifecycle import LLM_CLIENT_CONTEXT_KEY
from persona_chatbot.worker.lifecycle import SESSION_MAKER_CONTEXT_KEY


async def get_session(
    session_maker: async_sessionmaker[AsyncSession] = Context(
        SESSION_MAKER_CONTEXT_KEY
    ),
) -> AsyncIterator[AsyncSession]:
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_memory_service(
    session: AsyncSession = Depends(get_session),
    llm_client: LLMClient = Context(LLM_CLIENT_CONTEXT_KEY),
) -> MemoryService:
    return MemoryService(
        chat_repo=ChatRepo(session=session),
        message_repo=MessageRepo(session=session),
        memory_fact_repo=MemoryFactRepo(session=session),
        llm_client=llm_client,
    )
