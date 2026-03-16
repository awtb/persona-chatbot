from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from persona_chatbot.bot.states import UserState
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService

router = Router(name=__name__)


@router.message(
    UserState.chatting,
    Command("reset"),
)
async def reset_chat_context(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
) -> None:
    updated_user = await user_service.reset_chat_context(
        current_user=current_user,
    )
    current_user.active_chat_id = updated_user.active_chat_id
    await message.answer(
        "Context cleared. Started a new chat with the current avatar.",
    )
