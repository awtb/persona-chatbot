from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from persona_chatbot.db.models.base import BaseModel
from persona_chatbot.db.models.mixins import HasCreatedAt
from persona_chatbot.db.models.mixins import HasID

if TYPE_CHECKING:
    from persona_chatbot.db.models.avatar import Avatar
    from persona_chatbot.db.models.chat import Chat
    from persona_chatbot.db.models.message import Message
    from persona_chatbot.db.models.user import User


class MemoryFact(HasID, HasCreatedAt, BaseModel):
    __tablename__ = "memory_facts"
    __table_args__ = (
        Index("ix_memory_facts_user_id_avatar_id", "user_id", "avatar_id"),
        UniqueConstraint(
            "user_id",
            "avatar_id",
            "fact_key",
            name="uq_memory_facts_user_avatar_fact_key",
        ),
    )

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
    fact_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    fact_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    source_chat_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("chats.id"),
        nullable=True,
    )
    source_message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("messages.id"),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        back_populates="memory_facts",
        foreign_keys=[user_id],
    )
    avatar: Mapped[Avatar] = relationship(
        back_populates="memory_facts",
        foreign_keys=[avatar_id],
    )
    source_chat: Mapped[Chat | None] = relationship(
        back_populates="memory_facts",
        foreign_keys=[source_chat_id],
    )
    source_message: Mapped[Message | None] = relationship(
        back_populates="memory_facts",
        foreign_keys=[source_message_id],
    )
