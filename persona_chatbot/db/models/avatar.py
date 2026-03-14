from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from persona_chatbot.db.models.base import BaseModel
from persona_chatbot.db.models.mixins import HasCreatedAt
from persona_chatbot.db.models.mixins import HasID

if TYPE_CHECKING:
    from persona_chatbot.db.models.chat import Chat
    from persona_chatbot.db.models.memory_fact import MemoryFact
    from persona_chatbot.db.models.user import User


class Avatar(HasID, HasCreatedAt, BaseModel):
    __tablename__ = "avatars"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    current_for_users: Mapped[list[User]] = relationship(
        back_populates="current_avatar",
        foreign_keys="User.current_avatar_id",
    )
    chats: Mapped[list[Chat]] = relationship(
        back_populates="avatar",
        foreign_keys="Chat.avatar_id",
    )
    memory_facts: Mapped[list[MemoryFact]] = relationship(
        back_populates="avatar",
        foreign_keys="MemoryFact.avatar_id",
    )
