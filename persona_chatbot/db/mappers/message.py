from persona_chatbot.db.models.message import Message
from persona_chatbot.dto.message import MessageDTO
from persona_chatbot.dto.message import MessageUpdateDTO


def to_message_dto(message: Message) -> MessageDTO:
    return MessageDTO(
        id=message.id,
        chat_id=message.chat_id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


def apply_message_update_dto(
    message: Message,
    dto: MessageUpdateDTO,
) -> None:
    message.chat_id = dto.chat_id
    message.role = dto.role
    message.content = dto.content
