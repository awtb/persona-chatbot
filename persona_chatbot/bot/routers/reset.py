from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from persona_chatbot.bot.states import UserState
from persona_chatbot.common.exceptions import AvatarNotSelected
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService
from persona_chatbot.templates import Renderer

router = Router(name=__name__)
RESET_AVATAR_REQUIRED_TEMPLATE = "bot/reset_avatar_required.jinja2"


async def perform_reset(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
) -> None:
    try:
        await user_service.reset_chat_context(
            current_user=current_user,
        )
    except AvatarNotSelected:
        await message.answer(
            await Renderer.render(RESET_AVATAR_REQUIRED_TEMPLATE),
        )
        return

    await message.answer(
        "Context cleared. Started a new chat with the current avatar.",
    )


@router.message(
    UserState.chatting,
    Command("reset"),
)
async def reset_chat_context(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
) -> None:
    await perform_reset(
        message=message,
        current_user=current_user,
        user_service=user_service,
    )
