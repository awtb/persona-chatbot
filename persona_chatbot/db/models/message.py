from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from persona_chatbot.common.enums import MessageRole
from persona_chatbot.db.models.base import BaseModel
from persona_chatbot.db.models.mixins import HasCreatedAt
from persona_chatbot.db.models.mixins import HasID

if TYPE_CHECKING:
    from persona_chatbot.db.models.chat import Chat
    from persona_chatbot.db.models.memory_fact import MemoryFact


TBL_ARGS = (Index("ix_messages_chat_id_created_at", "chat_id", "created_at"),)


class Message(HasID, HasCreatedAt, BaseModel):
    __tablename__ = "messages"
    __table_args__ = TBL_ARGS

    chat_id: Mapped[UUID] = mapped_column(
        ForeignKey("chats.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        SQLAlchemyEnum(MessageRole, name="message_role"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chat: Mapped[Chat] = relationship(
        back_populates="messages",
        foreign_keys=[chat_id],
    )
    memory_facts: Mapped[list[MemoryFact]] = relationship(
        back_populates="source_message",
        foreign_keys="MemoryFact.source_message_id",
    )
