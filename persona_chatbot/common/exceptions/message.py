from uuid import UUID

from persona_chatbot.common.exceptions.base import NotFoundError


class MessageNotFound(NotFoundError):
    def __init__(
        self,
        message_id: UUID,
    ) -> None:
        super().__init__(
            f"Message with id={message_id} was not found.",
        )
        self.message_id = message_id
