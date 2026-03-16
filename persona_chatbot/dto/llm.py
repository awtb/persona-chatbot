from dataclasses import dataclass

from persona_chatbot.common.enums import MessageRole
from persona_chatbot.dto.base import BaseDTO


@dataclass
class LLMMessageDTO(BaseDTO):
    role: MessageRole
    content: str
