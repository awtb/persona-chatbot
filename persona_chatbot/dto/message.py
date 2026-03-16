from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from persona_chatbot.common.enums import MessageRole
from persona_chatbot.dto.base import BaseDTO


@dataclass
class MessageDTO(BaseDTO):
    id: UUID
    chat_id: UUID
    role: MessageRole
    content: str
    created_at: datetime


@dataclass
class MessageCreateDTO(BaseDTO):
    chat_id: UUID
    role: MessageRole
    content: str


@dataclass
class MessageUpdateDTO(BaseDTO):
    chat_id: UUID
    role: MessageRole
    content: str
