from persona_chatbot.db.models.chat import Chat
from persona_chatbot.dto.chat import ChatDTO
from persona_chatbot.dto.chat import ChatUpdateDTO


def to_chat_dto(chat: Chat) -> ChatDTO:
    return ChatDTO(
        id=chat.id,
        user_id=chat.user_id,
        avatar_id=chat.avatar_id,
        status=chat.status,
        message_count=chat.message_count,
        completed_turn_count=chat.completed_turn_count,
        created_at=chat.created_at,
        closed_at=chat.closed_at,
    )


def apply_chat_update_dto(
    chat: Chat,
    dto: ChatUpdateDTO,
) -> None:
    chat.user_id = dto.user_id
    chat.avatar_id = dto.avatar_id
    chat.status = dto.status
    chat.message_count = dto.message_count
    chat.completed_turn_count = dto.completed_turn_count
    chat.closed_at = dto.closed_at
