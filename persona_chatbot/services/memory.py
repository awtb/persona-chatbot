import hashlib
from uuid import UUID

import structlog

from persona_chatbot.common.enums import MessageRole
from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.memory import MemoryFactRepo
from persona_chatbot.db.repos.message import MessageRepo
from persona_chatbot.dto.chat import ChatDTO
from persona_chatbot.dto.memory import MemoryFactCreateDTO
from persona_chatbot.dto.memory import MemoryFactDTO
from persona_chatbot.dto.message import MessageDTO
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.schemas import ExtractedMemoryFactsSchema
from persona_chatbot.templates import Renderer

logger = structlog.get_logger(__name__)


class MemoryService:
    def __init__(
        self,
        chat_repo: ChatRepo,
        message_repo: MessageRepo,
        memory_fact_repo: MemoryFactRepo,
        llm_client: LLMClient,
    ) -> None:
        self._chat_repo = chat_repo
        self._message_repo = message_repo
        self._memory_fact_repo = memory_fact_repo
        self._llm_client = llm_client

    async def extract_facts(
        self,
        chat_id: UUID,
    ) -> None:
        chat = await self._chat_repo.get(chat_id=chat_id)
        turn = await self._load_recent_turn(chat_id=chat_id)
        if turn is None:
            logger.info(
                "Skipping memory fact extraction without a full recent turn",
                chat_id=chat_id,
            )
            return

        user_message, assistant_message = turn
        existing_facts = await self._memory_fact_repo.fetch_user_avatar_facts(
            user_id=chat.user_id,
            avatar_id=chat.avatar_id,
            limit=100,
        )
        analysis = await self._analyze_turn(
            user_message=user_message,
            assistant_message=assistant_message,
        )
        saved_facts = await self._save_facts(
            chat=chat,
            user_message=user_message,
            analysis=analysis,
        )
        self._log_analysis_result(
            chat_id=chat_id,
            user_id=chat.user_id,
            avatar_id=chat.avatar_id,
            user_message=user_message,
            assistant_message=assistant_message,
            existing_facts_count=len(existing_facts),
            analysis=analysis,
            saved_facts_count=len(saved_facts),
        )

    async def _load_recent_turn(
        self,
        chat_id: UUID,
    ) -> tuple[MessageDTO, MessageDTO] | None:
        messages = await self._message_repo.fetch_recent_chat_messages(
            chat_id=chat_id,
            limit=2,
        )
        user_message, assistant_message = self._resolve_recent_turn(messages)
        if user_message is None or assistant_message is None:
            return None

        return user_message, assistant_message

    async def _analyze_turn(
        self,
        *,
        user_message: MessageDTO,
        assistant_message: MessageDTO,
    ) -> ExtractedMemoryFactsSchema:
        system_prompt = await Renderer.render(
            "prompts/memory/extract_facts_system.jinja2",
        )
        prompt = await Renderer.render(
            "prompts/memory/extract_facts_user.jinja2",
            user_message=user_message,
            assistant_message=assistant_message,
        )
        return await self._llm_client.complete(
            system_prompt=system_prompt,
            message=prompt,
            response_format=ExtractedMemoryFactsSchema,
        )

    async def _save_facts(
        self,
        *,
        chat: ChatDTO,
        user_message: MessageDTO,
        analysis: ExtractedMemoryFactsSchema,
    ) -> list[MemoryFactDTO]:
        facts_by_key: dict[str, MemoryFactCreateDTO] = {}
        for fact in analysis.facts:
            fact_key = self._build_fact_key(
                kind=fact.kind,
                content=fact.content,
            )
            facts_by_key[fact_key] = MemoryFactCreateDTO(
                user_id=chat.user_id,
                avatar_id=chat.avatar_id,
                fact_text=fact.content,
                fact_key=fact_key,
                source_chat_id=chat.id,
                source_message_id=user_message.id,
            )

        return await self._memory_fact_repo.upsert_many(
            dtos=list(facts_by_key.values()),
        )

    @staticmethod
    def _log_analysis_result(
        *,
        chat_id: UUID,
        user_id: UUID,
        avatar_id: UUID,
        user_message: MessageDTO,
        assistant_message: MessageDTO,
        existing_facts_count: int,
        analysis: ExtractedMemoryFactsSchema,
        saved_facts_count: int,
    ) -> None:
        logger.info(
            "Analyzed recent turn for memory extraction",
            chat_id=chat_id,
            user_id=user_id,
            avatar_id=avatar_id,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            existing_facts_count=existing_facts_count,
            saved_facts_count=saved_facts_count,
            extracted_facts=analysis.model_dump(mode="json"),
        )

    @staticmethod
    def _resolve_recent_turn(
        messages: list[MessageDTO],
    ) -> tuple[MessageDTO | None, MessageDTO | None]:
        user_message: MessageDTO | None = None
        assistant_message: MessageDTO | None = None

        for message in messages:
            if message.role is MessageRole.USER:
                user_message = message
                continue

            if message.role is MessageRole.ASSISTANT:
                assistant_message = message

        return user_message, assistant_message

    @staticmethod
    def _build_fact_key(
        *,
        kind: str,
        content: str,
    ) -> str:
        normalized = " ".join(content.lower().split())
        key_source = f"{kind}:{normalized}"
        return hashlib.sha256(key_source.encode("utf-8")).hexdigest()
