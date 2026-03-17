from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from persona_chatbot.bot.keyboards import build_menu_keyboard
from persona_chatbot.bot.routers.avatar import show_avatar_selection
from persona_chatbot.bot.states import UserState
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService
from persona_chatbot.templates import Renderer

router = Router(name=__name__)

START_TEMPLATE = "bot/start.jinja2"


async def _send_start_message(
    message: Message,
    *,
    needs_avatar_selection: bool,
) -> None:
    text = await Renderer.render(
        START_TEMPLATE,
        needs_avatar_selection=needs_avatar_selection,
    )
    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_menu_keyboard(),
    )


async def show_start(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
    state: FSMContext,
) -> None:
    needs_avatar_selection = current_user.current_avatar_id is None
    await _send_start_message(
        message=message,
        needs_avatar_selection=needs_avatar_selection,
    )
    if needs_avatar_selection:
        await show_avatar_selection(
            message=message,
            user_service=user_service,
            state=state,
        )
        return

    await state.set_state(UserState.chatting)


@router.message(CommandStart())
async def start(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await show_start(
        message=message,
        current_user=current_user,
        user_service=user_service,
        state=state,
    )
