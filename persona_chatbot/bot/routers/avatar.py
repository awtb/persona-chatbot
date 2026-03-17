from aiogram import F
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from persona_chatbot.bot.callbacks import AVATAR_BACK_CALLBACK
from persona_chatbot.bot.callbacks import AVATAR_PREVIEW_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import AVATAR_SELECT_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import parse_avatar_preview_callback_data
from persona_chatbot.bot.callbacks import parse_avatar_select_callback_data
from persona_chatbot.bot.keyboards import build_avatar_keyboard
from persona_chatbot.bot.keyboards import build_avatar_preview_keyboard
from persona_chatbot.bot.states import UserState
from persona_chatbot.common.exceptions import AvatarNotFound
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.avatar import AvatarService
from persona_chatbot.services.user import UserService
from persona_chatbot.templates import Renderer

router = Router(name=__name__)
AVATAR_PREVIEW_TEMPLATE = "bot/avatar_preview.jinja2"
AVATAR_SELECTED_TEMPLATE = "bot/avatar_selected.jinja2"
AVATAR_SELECTION_TEXT = "Please choose an avatar to start chatting:"
AVATAR_SELECTION_REQUIRED_TEXT = (
    "You are currently selecting an avatar. "
    "Please choose one of the available avatars."
)


async def _edit_avatar_selection(
    message: Message,
    user_service: UserService,
) -> None:
    avatars = await user_service.list_available_avatars()
    if not avatars:
        await message.edit_text(
            "No avatars are available yet. Please try again later.",
        )
        return

    await message.edit_text(
        AVATAR_SELECTION_TEXT,
        reply_markup=build_avatar_keyboard(avatars=avatars),
    )


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
        AVATAR_SELECTION_TEXT,
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


@router.message(UserState.choosing_avatar)
async def prompt_avatar_selection(
    message: Message,
    user_service: UserService,
) -> None:
    avatars = await user_service.list_available_avatars()
    if not avatars:
        await message.answer(
            "No avatars are available yet. Please try again later.",
        )
        return

    await message.answer(
        AVATAR_SELECTION_REQUIRED_TEXT,
        reply_markup=build_avatar_keyboard(avatars=avatars),
    )


@router.callback_query(
    UserState.choosing_avatar,
    F.data.startswith(AVATAR_PREVIEW_CALLBACK_PREFIX),
)
async def preview_avatar(
    callback_query: CallbackQuery,
    avatar_service: AvatarService,
) -> None:
    avatar_id = parse_avatar_preview_callback_data(
        callback_data=callback_query.data,
    )
    if avatar_id is None:
        await callback_query.answer(
            "Invalid avatar selection.",
            show_alert=True,
        )
        return

    try:
        avatar = await avatar_service.get_avatar(
            avatar_id=avatar_id,
        )
    except AvatarNotFound:
        await callback_query.answer(
            "Selected avatar does not exist.",
            show_alert=True,
        )
        return

    message = callback_query.message
    if message is None:
        await callback_query.answer()
        return

    text = await Renderer.render(
        AVATAR_PREVIEW_TEMPLATE,
        avatar=avatar,
    )
    await message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_avatar_preview_keyboard(avatar=avatar),
    )
    await callback_query.answer()


@router.callback_query(
    UserState.choosing_avatar,
    F.data == AVATAR_BACK_CALLBACK,
)
async def back_to_avatar_selection(
    callback_query: CallbackQuery,
    user_service: UserService,
) -> None:
    message = callback_query.message
    if message is None:
        await callback_query.answer()
        return

    await _edit_avatar_selection(
        message=message,
        user_service=user_service,
    )
    await callback_query.answer()


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
    message = callback_query.message
    if message is None:
        return

    text = await Renderer.render(
        AVATAR_SELECTED_TEMPLATE,
        avatar=avatar,
    )
    await message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
    )
