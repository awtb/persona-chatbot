from uuid import UUID

from sqlalchemy import select

from persona_chatbot.common.exceptions import MessageNotFound
from persona_chatbot.db.mappers.message import apply_message_update_dto
from persona_chatbot.db.mappers.message import to_message_dto
from persona_chatbot.db.models.message import Message
from persona_chatbot.db.repos.base import BaseRepository
from persona_chatbot.dto.base import PageDTO
from persona_chatbot.dto.message import MessageCreateDTO
from persona_chatbot.dto.message import MessageDTO
from persona_chatbot.dto.message import MessageUpdateDTO


class MessageRepo(BaseRepository):
    async def get(
        self,
        message_id: UUID,
    ) -> MessageDTO:
        query = select(Message).where(Message.id == message_id)
        message = await self._session.scalar(query)
        if message is None:
            raise MessageNotFound(message_id=message_id)

        return to_message_dto(message)

    async def create(
        self,
        dto: MessageCreateDTO,
    ) -> MessageDTO:
        message = Message(
            chat_id=dto.chat_id,
            role=dto.role,
            content=dto.content,
        )
        self._session.add(message)
        await self._session.flush()

        return to_message_dto(message)

    async def update_message(
        self,
        message_id: UUID,
        dto: MessageUpdateDTO,
    ) -> MessageDTO | None:
        query = select(Message).where(Message.id == message_id)
        message = await self._session.scalar(query)
        if message is None:
            return None

        apply_message_update_dto(message=message, dto=dto)
        await self._session.flush()

        return to_message_dto(message)

    async def delete(
        self,
        message_id: UUID,
    ) -> bool:
        query = select(Message).where(Message.id == message_id)
        message = await self._session.scalar(query)
        if message is None:
            return False

        await self._session.delete(message)
        await self._session.flush()

        return True

    async def fetch_chat_messages(
        self,
        chat_id: UUID,
        page: int = 1,
        page_size: int = 100,
    ) -> PageDTO[MessageDTO]:
        query = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        return await self._fetch(
            query=query,
            page=page,
            page_size=page_size,
            mapper_fn=to_message_dto,
        )

    async def fetch_recent_chat_messages(
        self,
        chat_id: UUID,
        limit: int = 20,
    ) -> list[MessageDTO]:
        query = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(query)).scalars().all()

        # Preserve chronological order for LLM context.
        return [to_message_dto(item) for item in reversed(rows)]
