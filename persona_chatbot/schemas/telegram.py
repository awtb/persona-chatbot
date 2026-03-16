from typing import Any

from pydantic import BaseModel


class TelegramUpdateTaskSchema(BaseModel):
    request_id: str
    update: dict[str, Any]
