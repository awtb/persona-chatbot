from persona_chatbot.db.models.user import User
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.dto.user import UserUpdateDTO


def to_user_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        telegram_user_id=user.telegram_user_id,
        current_avatar_id=user.current_avatar_id,
        active_chat_id=user.active_chat_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def apply_user_update_dto(
    user: User,
    dto: UserUpdateDTO,
) -> None:
    user.telegram_user_id = dto.telegram_user_id
    user.current_avatar_id = dto.current_avatar_id
    user.active_chat_id = dto.active_chat_id
