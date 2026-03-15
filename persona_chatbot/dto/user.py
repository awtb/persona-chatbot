from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from persona_chatbot.dto.base import BaseDTO


@dataclass
class UserDTO(BaseDTO):
    id: UUID
    telegram_user_id: int
    current_avatar_id: UUID | None
    active_chat_id: UUID | None
    created_at: datetime
    updated_at: datetime


@dataclass
class UserCreateDTO(BaseDTO):
    telegram_user_id: int
    current_avatar_id: UUID | None = None
    active_chat_id: UUID | None = None


@dataclass
class UserUpdateDTO(BaseDTO):
    telegram_user_id: int
    current_avatar_id: UUID | None
    active_chat_id: UUID | None
