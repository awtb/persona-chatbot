from collections.abc import AsyncIterator
from uuid import UUID

import structlog
from faststream.redis import RedisBroker

from persona_chatbot.common.constants import FALLBACK_RESPONSE_TEXT
from persona_chatbot.common.enums import MessageRole
from persona_chatbot.common.exceptions import ActiveChatNotSelected
from persona_chatbot.common.exceptions import LLMProviderError
from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.memory import MemoryFactRepo
from persona_chatbot.db.repos.message import MessageRepo
from persona_chatbot.dto.avatar import AvatarDTO
from persona_chatbot.dto.base import PageDTO
from persona_chatbot.dto.chat import ChatDTO
from persona_chatbot.dto.chat import ChatReplyStream
from persona_chatbot.dto.chat import ChatUpdateDTO
from persona_chatbot.dto.llm import LLMMessageDTO
from persona_chatbot.dto.memory import MemoryFactDTO
from persona_chatbot.dto.message import MessageCreateDTO
from persona_chatbot.dto.message import MessageDTO
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.schemas import ExtractMemoryFactsTaskSchema
from persona_chatbot.services.avatar import AvatarService
from persona_chatbot.templates import Renderer
from persona_chatbot.worker.queues import EXTRACT_MEMORY_FACTS_QUEUE

MIN_MEMORY_SOURCE_MESSAGE_LEN = 10
SYSTEM_PROMPT_MEMORY_FACTS_LIMIT = 10
SYSTEM_PROMPT_TEMPLATE = "prompts/system/system_prompt_base.jinja2"

logger = structlog.get_logger(__name__)


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        avatar_service: AvatarService,
        chat_repo: ChatRepo,
        message_repo: MessageRepo,
        memory_fact_repo: MemoryFactRepo,
        broker: RedisBroker,
        max_previous_messages: int,
    ) -> None:
        self._llm_client = llm_client
        self._avatar_service = avatar_service
        self._chat_repo = chat_repo
        self._message_repo = message_repo
        self._memory_fact_repo = memory_fact_repo
        self._broker = broker
        self._max_previous_messages = max_previous_messages

    def stream_reply_to_message(
        self,
        current_user: UserDTO,
        message: str,
    ) -> ChatReplyStream:
        async def stream_with_fallback() -> AsyncIterator[str]:
            chat = await self._require_active_chat(current_user=current_user)
            previous_messages = await self._load_previous_messages(
                chat_id=chat.id,
                limit=self._max_previous_messages,
            )
            chat, user_message = await self._save_message(
                chat=chat,
                role=MessageRole.USER,
                content=message,
            )
            system_prompt = await self._build_system_prompt(
                current_user=current_user,
            )
            assistant_chunks: list[str] = []
            async for chunk in self._stream_assistant_chunks(
                message=message,
                system_prompt=system_prompt,
                previous_messages=previous_messages,
            ):
                assistant_chunks.append(chunk)
                yield chunk

            assistant_message_text = "".join(assistant_chunks).strip()
            if not assistant_message_text:
                return

            chat, assistant_message = await self._save_message(
                chat=chat,
                role=MessageRole.ASSISTANT,
                content=assistant_message_text,
            )

            await self._maybe_enqueue_extract_fact_task(
                chat=chat,
                user_message=user_message,
                assistant_message=assistant_message,
            )

        return ChatReplyStream(chunks=stream_with_fallback())

    async def get_recent_history(
        self,
        current_user: UserDTO,
        limit: int = 10,
    ) -> list[MessageDTO]:
        chat = await self._require_active_chat(current_user=current_user)
        return await self._message_repo.fetch_recent_chat_messages(
            chat_id=chat.id,
            limit=limit,
        )

    async def get_avatar_facts(
        self,
        current_user: UserDTO,
        avatar_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[AvatarDTO, PageDTO[MemoryFactDTO]]:
        avatar = await self._avatar_service.get_avatar(
            avatar_id=avatar_id,
        )
        facts_page = await self._memory_fact_repo.fetch_user_avatar_facts_page(
            user_id=current_user.id,
            avatar_id=avatar.id,
            page=page,
            page_size=page_size,
        )
        return avatar, facts_page

    async def _maybe_enqueue_extract_fact_task(
        self,
        chat: ChatDTO,
        user_message: MessageDTO,
        assistant_message: MessageDTO,
    ) -> None:
        if len(user_message.content.strip()) <= MIN_MEMORY_SOURCE_MESSAGE_LEN:
            return

        payload = ExtractMemoryFactsTaskSchema(
            chat_id=chat.id,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            user_message_text=user_message.content,
            assistant_message_text=assistant_message.content,
        )
        await self._broker.publish(
            payload.model_dump(mode="json"),
            list=EXTRACT_MEMORY_FACTS_QUEUE,
        )

    async def _build_system_prompt(
        self,
        current_user: UserDTO,
    ) -> str:
        avatar = await self._avatar_service.resolve_avatar(
            current_user=current_user,
        )
        memory_facts = await self._load_memory_facts(current_user=current_user)
        logger.debug(
            "Injecting memory facts into system prompt",
            user_id=current_user.id,
            avatar_id=avatar.id,
            memory_facts_count=len(memory_facts),
            memory_fact_ids=[fact.id for fact in memory_facts],
        )

        system_prompt = await Renderer.render(
            SYSTEM_PROMPT_TEMPLATE,
            avatar=avatar,
            avatar_prompt=avatar.system_prompt,
            memory_facts=memory_facts,
        )
        logger.debug(
            "Built system prompt",
            user_id=current_user.id,
            avatar_id=avatar.id,
            system_prompt_chars=len(system_prompt),
            memory_facts_count=len(memory_facts),
        )
        return system_prompt

    async def _load_memory_facts(
        self,
        current_user: UserDTO,
    ) -> list[MemoryFactDTO]:
        if current_user.current_avatar_id is None:
            logger.debug(
                "Skipping memory fact injection without selected avatar",
                user_id=current_user.id,
            )
            return []

        memory_facts = await self._memory_fact_repo.fetch_user_avatar_facts(
            user_id=current_user.id,
            avatar_id=current_user.current_avatar_id,
            limit=SYSTEM_PROMPT_MEMORY_FACTS_LIMIT,
        )
        logger.debug(
            "Loaded memory facts for system prompt",
            user_id=current_user.id,
            avatar_id=current_user.current_avatar_id,
            memory_facts_count=len(memory_facts),
            memory_fact_ids=[fact.id for fact in memory_facts],
        )
        return memory_facts

    async def _require_active_chat(
        self,
        current_user: UserDTO,
    ) -> ChatDTO:
        if current_user.active_chat_id is None:
            raise ActiveChatNotSelected()

        return await self._chat_repo.get(
            chat_id=current_user.active_chat_id,
        )

    async def _load_previous_messages(
        self,
        chat_id: UUID,
        limit: int,
    ) -> list[LLMMessageDTO]:
        recent_messages = await self._message_repo.fetch_recent_chat_messages(
            chat_id=chat_id,
            limit=limit,
        )
        return [
            LLMMessageDTO(
                role=message.role,
                content=message.content,
            )
            for message in recent_messages
        ]

    async def _save_message(
        self,
        chat: ChatDTO,
        role: MessageRole,
        content: str,
    ) -> tuple[ChatDTO, MessageDTO]:
        message = await self._message_repo.create(
            dto=MessageCreateDTO(
                chat_id=chat.id,
                role=role,
                content=content,
            ),
        )
        updated_chat = await self._chat_repo.update_chat(
            chat_id=chat.id,
            dto=ChatUpdateDTO(
                user_id=chat.user_id,
                avatar_id=chat.avatar_id,
                status=chat.status,
                message_count=chat.message_count + 1,
                completed_turn_count=(
                    chat.completed_turn_count
                    + (1 if role is MessageRole.ASSISTANT else 0)
                ),
                closed_at=chat.closed_at,
            ),
        )
        if updated_chat is None:
            return chat, message

        return updated_chat, message

    async def _stream_assistant_chunks(
        self,
        message: str,
        system_prompt: str,
        previous_messages: list[LLMMessageDTO],
    ) -> AsyncIterator[str]:
        try:
            async for chunk in self._llm_client.stream_reply(
                message=message,
                system_prompt=system_prompt,
                previous_messages=previous_messages,
            ):
                yield chunk
        except LLMProviderError:
            yield FALLBACK_RESPONSE_TEXT
