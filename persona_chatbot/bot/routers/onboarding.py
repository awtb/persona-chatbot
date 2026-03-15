from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from persona_chatbot.dto.user import UserDTO

router = Router(name=__name__)


@router.message(CommandStart())
async def start(
    message: Message,
    current_user: UserDTO,
) -> None:
    await message.answer(
        (
            "Hello!\n"
            f"id={current_user.id}\n"
            f"telegram_user_id={current_user.telegram_user_id}\n"
            f"current_avatar_id={current_user.current_avatar_id}\n"
            f"active_chat_id={current_user.active_chat_id}\n"
            f"created_at={current_user.created_at.isoformat()}\n"
            f"updated_at={current_user.updated_at.isoformat()}"
        ),
    )
