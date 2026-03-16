from uuid import UUID

from persona_chatbot.common.exceptions.base import NotFoundError
from persona_chatbot.common.exceptions.base import PersonaChatbotError


class ChatNotFound(NotFoundError):
    def __init__(
        self,
        chat_id: UUID,
    ) -> None:
        super().__init__(
            f"Chat with id={chat_id} was not found.",
        )
        self.chat_id = chat_id


class ActiveChatNotSelected(PersonaChatbotError):
    def __init__(self) -> None:
        super().__init__(
            "Current user does not have an active chat.",
        )
