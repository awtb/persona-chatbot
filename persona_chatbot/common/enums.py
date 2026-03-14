from enum import StrEnum


class ChatStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


__all__ = [
    "ChatStatus",
    "MessageRole",
]
