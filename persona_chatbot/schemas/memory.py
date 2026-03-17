from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ExtractMemoryFactsTaskSchema(BaseModel):
    chat_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    user_message_text: str
    assistant_message_text: str


class ExtractedMemoryFactSchema(BaseModel):
    kind: Literal[
        "profile",
        "preference",
        "goal",
        "project",
        "constraint",
        "workflow",
    ]
    content: str


class ExtractedMemoryFactsSchema(BaseModel):
    facts: list[ExtractedMemoryFactSchema]
