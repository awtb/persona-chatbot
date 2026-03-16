from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ExtractMemoryFactsTaskSchema(BaseModel):
    chat_id: UUID


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
