from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from persona_chatbot.db.models.base import BaseModel
from persona_chatbot.db.models.mixins import HasID
from persona_chatbot.db.models.mixins import HasTimestamps

if TYPE_CHECKING:
    from persona_chatbot.db.models.avatar import Avatar
    from persona_chatbot.db.models.chat import Chat
    from persona_chatbot.db.models.memory_fact import MemoryFact


class User(HasID, HasTimestamps, BaseModel):
    __tablename__ = "users"

    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
    )
    current_avatar_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("avatars.id"),
        nullable=True,
    )
    active_chat_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("chats.id"),
        nullable=True,
    )

    current_avatar: Mapped[Avatar | None] = relationship(
        foreign_keys=[current_avatar_id],
    )
    active_chat: Mapped[Chat | None] = relationship(
        back_populates="active_for_users",
        foreign_keys=[active_chat_id],
        post_update=True,
    )
    chats: Mapped[list[Chat]] = relationship(
        back_populates="user",
        foreign_keys="Chat.user_id",
    )
    memory_facts: Mapped[list[MemoryFact]] = relationship(
        back_populates="user",
        foreign_keys="MemoryFact.user_id",
    )
