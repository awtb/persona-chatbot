from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from persona_chatbot.common.enums import ChatStatus
from persona_chatbot.db.models.base import BaseModel
from persona_chatbot.db.models.mixins import HasClosedAt
from persona_chatbot.db.models.mixins import HasCreatedAt
from persona_chatbot.db.models.mixins import HasID

if TYPE_CHECKING:
    from persona_chatbot.db.models.avatar import Avatar
    from persona_chatbot.db.models.memory_fact import MemoryFact
    from persona_chatbot.db.models.message import Message
    from persona_chatbot.db.models.user import User


class Chat(HasID, HasCreatedAt, HasClosedAt, BaseModel):
    __tablename__ = "chats"
    __table_args__ = (Index("ix_chats_user_id_status", "user_id", "status"),)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    avatar_id: Mapped[UUID] = mapped_column(
        ForeignKey("avatars.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[ChatStatus] = mapped_column(
        SQLAlchemyEnum(ChatStatus, name="chat_status"),
        default=ChatStatus.ACTIVE,
        nullable=False,
    )
    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    completed_turn_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    user: Mapped[User] = relationship(
        back_populates="chats",
        foreign_keys=[user_id],
    )
    avatar: Mapped[Avatar] = relationship(
        back_populates="chats",
        foreign_keys=[avatar_id],
    )
    messages: Mapped[list[Message]] = relationship(
        back_populates="chat",
        foreign_keys="Message.chat_id",
        order_by="Message.created_at",
    )
    memory_facts: Mapped[list[MemoryFact]] = relationship(
        back_populates="source_chat",
        foreign_keys="MemoryFact.source_chat_id",
    )
