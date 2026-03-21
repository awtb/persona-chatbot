from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from persona_chatbot.dto.base import BaseDTO


@dataclass
class AvatarDTO(BaseDTO):
    id: UUID
    name: str
    description: str
    system_prompt: str
    temperature: float | None
    created_at: datetime
