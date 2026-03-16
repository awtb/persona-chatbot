from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from persona_chatbot.common.enums import ChatStatus
from persona_chatbot.dto.base import BaseDTO


class ChatReplyStream(BaseDTO):
    def __init__(
        self,
        chunks: AsyncIterator[str],
    ) -> None:
        self._chunks = chunks

    def __aiter__(self) -> AsyncIterator[str]:
        return self._chunks


@dataclass
class ChatDTO(BaseDTO):
    id: UUID
    user_id: UUID
    avatar_id: UUID
    status: ChatStatus
    message_count: int
    completed_turn_count: int
    created_at: datetime
    closed_at: datetime | None


@dataclass
class ChatCreateDTO(BaseDTO):
    user_id: UUID
    avatar_id: UUID
    status: ChatStatus = ChatStatus.ACTIVE
    message_count: int = 0
    completed_turn_count: int = 0
    closed_at: datetime | None = None


@dataclass
class ChatUpdateDTO(BaseDTO):
    user_id: UUID
    avatar_id: UUID
    status: ChatStatus
    message_count: int
    completed_turn_count: int
    closed_at: datetime | None
