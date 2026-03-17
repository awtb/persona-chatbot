from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from persona_chatbot.dto.base import BaseDTO


@dataclass
class MemoryFactDTO(BaseDTO):
    id: UUID
    user_id: UUID
    avatar_id: UUID
    fact_text: str
    fact_key: str
    source_chat_id: UUID | None
    created_at: datetime


@dataclass
class MemoryFactCreateDTO(BaseDTO):
    user_id: UUID
    avatar_id: UUID
    fact_text: str
    fact_key: str
    source_chat_id: UUID | None = None


@dataclass
class MemoryFactUpdateDTO(BaseDTO):
    user_id: UUID
    avatar_id: UUID
    fact_text: str
    fact_key: str
    source_chat_id: UUID | None
