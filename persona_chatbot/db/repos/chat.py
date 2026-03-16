from uuid import UUID

from sqlalchemy import select

from persona_chatbot.common.exceptions import ChatNotFound
from persona_chatbot.db.mappers.chat import apply_chat_update_dto
from persona_chatbot.db.mappers.chat import to_chat_dto
from persona_chatbot.db.models.chat import Chat
from persona_chatbot.db.repos.base import BaseRepository
from persona_chatbot.dto.base import PageDTO
from persona_chatbot.dto.chat import ChatCreateDTO
from persona_chatbot.dto.chat import ChatDTO
from persona_chatbot.dto.chat import ChatUpdateDTO


class ChatRepo(BaseRepository):
    async def get(
        self,
        chat_id: UUID,
    ) -> ChatDTO:
        query = select(Chat).where(Chat.id == chat_id)
        chat = await self._session.scalar(query)
        if chat is None:
            raise ChatNotFound(chat_id=chat_id)

        return to_chat_dto(chat)

    async def create(
        self,
        dto: ChatCreateDTO,
    ) -> ChatDTO:
        chat = Chat(
            user_id=dto.user_id,
            avatar_id=dto.avatar_id,
            status=dto.status,
            message_count=dto.message_count,
            completed_turn_count=dto.completed_turn_count,
            closed_at=dto.closed_at,
        )
        self._session.add(chat)
        await self._session.flush()

        return to_chat_dto(chat)

    async def update_chat(
        self,
        chat_id: UUID,
        dto: ChatUpdateDTO,
    ) -> ChatDTO | None:
        query = select(Chat).where(Chat.id == chat_id)
        chat = await self._session.scalar(query)
        if chat is None:
            return None

        apply_chat_update_dto(chat=chat, dto=dto)
        await self._session.flush()

        return to_chat_dto(chat)

    async def delete(
        self,
        chat_id: UUID,
    ) -> bool:
        query = select(Chat).where(Chat.id == chat_id)
        chat = await self._session.scalar(query)
        if chat is None:
            return False

        await self._session.delete(chat)
        await self._session.flush()

        return True

    async def fetch_user_chats(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> PageDTO[ChatDTO]:
        query = select(Chat).where(Chat.user_id == user_id)
        query = query.order_by(Chat.created_at.desc())
        return await self._fetch(
            query=query,
            page=page,
            page_size=page_size,
            mapper_fn=to_chat_dto,
        )
