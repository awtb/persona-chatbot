from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from persona_chatbot.bot.states import UserState
from persona_chatbot.common.enums import MessageRole
from persona_chatbot.dto.message import MessageDTO
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.chat import ChatService
from persona_chatbot.templates import Renderer

router = Router(name=__name__)

HISTORY_LIMIT = 10


async def _render_history(
    messages: list[MessageDTO],
) -> str:
    return await Renderer.render(
        "bot/messages_history.jinja2",
        messages=messages,
        MessageRole=MessageRole,
    )


async def show_history(
    message: Message,
    current_user: UserDTO,
    chat_service: ChatService,
) -> None:
    messages = await chat_service.get_recent_history(
        current_user=current_user,
        limit=HISTORY_LIMIT,
    )
    await message.answer(
        await _render_history(messages=messages),
        parse_mode=ParseMode.HTML,
    )


@router.message(
    UserState.chatting,
    Command("history"),
)
async def history(
    message: Message,
    current_user: UserDTO,
    chat_service: ChatService,
) -> None:
    await show_history(
        message=message,
        current_user=current_user,
        chat_service=chat_service,
    )
