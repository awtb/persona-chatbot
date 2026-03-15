from persona_chatbot.common.exceptions.base import NotFoundError


class UserNotFound(NotFoundError):
    def __init__(self, telegram_user_id: int) -> None:
        super().__init__(
            f"User with telegram_user_id={telegram_user_id} was not found.",
        )
        self.telegram_user_id = telegram_user_id
