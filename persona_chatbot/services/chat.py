from collections.abc import AsyncIterator
from uuid import UUID

from persona_chatbot.common.enums import MessageRole
from persona_chatbot.common.exceptions import ActiveChatNotSelected
from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.message import MessageRepo
from persona_chatbot.dto.chat import ChatDTO
from persona_chatbot.dto.chat import ChatReplyStream
from persona_chatbot.dto.chat import ChatUpdateDTO
from persona_chatbot.dto.llm import LLMMessageDTO
from persona_chatbot.dto.message import MessageCreateDTO
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.services.avatar import AvatarService

FALLBACK_RESPONSE = "I could not generate a response right now."
MAX_PREVIOUS_MESSAGES = 20


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        avatar_service: AvatarService,
        chat_repo: ChatRepo,
        message_repo: MessageRepo,
    ) -> None:
        self._llm_client = llm_client
        self._avatar_service = avatar_service
        self._chat_repo = chat_repo
        self._message_repo = message_repo

    def stream_reply_to_message(
        self,
        current_user: UserDTO,
        message: str,
    ) -> ChatReplyStream:
        async def stream_with_fallback() -> AsyncIterator[str]:
            chat = await self._require_active_chat(current_user=current_user)
            previous_messages = await self._load_previous_messages(
                chat_id=chat.id,
                limit=MAX_PREVIOUS_MESSAGES,
            )
            chat = await self._save_message(
                chat=chat,
                role=MessageRole.USER,
                content=message,
            )
            system_prompt = await self._avatar_service.resolve_system_prompt(
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

            assistant_message = "".join(assistant_chunks).strip()
            if not assistant_message:
                return

            await self._save_message(
                chat=chat,
                role=MessageRole.ASSISTANT,
                content=assistant_message,
            )

        return ChatReplyStream(chunks=stream_with_fallback())

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
    ) -> ChatDTO:
        await self._message_repo.create(
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
            return chat

        return updated_chat

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
        except Exception:
            yield FALLBACK_RESPONSE
