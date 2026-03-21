from __future__ import annotations

from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from persona_chatbot.db.models.base import BaseModel
from persona_chatbot.db.models.mixins import HasCreatedAt
from persona_chatbot.db.models.mixins import HasID


class Avatar(HasID, HasCreatedAt, BaseModel):
    __tablename__ = "avatars"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
