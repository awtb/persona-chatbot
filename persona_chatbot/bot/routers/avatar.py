from aiogram import F
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from persona_chatbot.bot.callbacks import AVATAR_SELECT_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import parse_avatar_select_callback_data
from persona_chatbot.bot.keyboards import build_avatar_keyboard
from persona_chatbot.bot.states import UserState
from persona_chatbot.common.exceptions import AvatarNotFound
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService
from persona_chatbot.templates import Renderer

router = Router(name=__name__)
AVATAR_SELECTED_TEMPLATE = "bot/avatar_selected.jinja2"


async def show_avatar_selection(
    message: Message,
    user_service: UserService,
    state: FSMContext,
) -> None:
    avatars = await user_service.list_available_avatars()
    await state.set_state(UserState.choosing_avatar)
    if not avatars:
        await message.answer(
            "No avatars are available yet. Please try again later.",
        )
        return

    await message.answer(
        "Please choose an avatar to start chatting:",
        reply_markup=build_avatar_keyboard(avatars=avatars),
    )


@router.message(Command("avatars"))
async def avatars(
    message: Message,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await show_avatar_selection(
        message=message,
        user_service=user_service,
        state=state,
    )


@router.callback_query(
    UserState.choosing_avatar,
    F.data.startswith(AVATAR_SELECT_CALLBACK_PREFIX),
)
async def select_avatar(
    callback_query: CallbackQuery,
    current_user: UserDTO,
    user_service: UserService,
    state: FSMContext,
) -> None:
    avatar_id = parse_avatar_select_callback_data(
        callback_data=callback_query.data,
    )
    if avatar_id is None:
        await callback_query.answer(
            "Invalid avatar selection.",
            show_alert=True,
        )
        return

    try:
        avatar = await user_service.select_avatar(
            current_user=current_user,
            avatar_id=avatar_id,
        )
    except AvatarNotFound:
        await callback_query.answer(
            "Selected avatar does not exist.",
            show_alert=True,
        )
        return

    await state.set_state(UserState.chatting)
    await callback_query.answer("Avatar selected.")
    if callback_query.message is not None:
        text = await Renderer.render(
            AVATAR_SELECTED_TEMPLATE,
            avatar=avatar,
        )
        await callback_query.message.answer(
            text,
            parse_mode=ParseMode.HTML,
        )
