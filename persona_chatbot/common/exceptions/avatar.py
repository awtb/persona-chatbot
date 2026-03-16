from uuid import UUID

from persona_chatbot.common.exceptions.base import NotFoundError
from persona_chatbot.common.exceptions.base import PersonaChatbotError


class AvatarNotFound(NotFoundError):
    def __init__(
        self,
        avatar_id: UUID,
    ) -> None:
        super().__init__(
            f"Avatar with id={avatar_id} was not found.",
        )
        self.avatar_id = avatar_id


class AvatarNotSelected(PersonaChatbotError):
    def __init__(self) -> None:
        super().__init__(
            "Current user does not have a selected avatar.",
        )
