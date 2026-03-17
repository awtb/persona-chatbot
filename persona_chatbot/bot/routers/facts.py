from uuid import UUID

from aiogram import F
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message

from persona_chatbot.bot.callbacks import FACTS_AVATAR_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import FACTS_MENU_CALLBACK
from persona_chatbot.bot.callbacks import FACTS_PAGE_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import parse_facts_avatar_callback_data
from persona_chatbot.bot.callbacks import parse_facts_page_callback_data
from persona_chatbot.bot.keyboards import build_facts_avatars_keyboard
from persona_chatbot.bot.keyboards import build_facts_pagination_keyboard
from persona_chatbot.bot.states import UserState
from persona_chatbot.common.exceptions import AvatarNotFound
from persona_chatbot.dto.avatar import AvatarDTO
from persona_chatbot.dto.base import PageDTO
from persona_chatbot.dto.memory import MemoryFactDTO
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.chat import ChatService
from persona_chatbot.services.user import UserService
from persona_chatbot.templates import Renderer

router = Router(name=__name__)

FACTS_PAGE_SIZE = 20
FACTS_TEMPLATE = "bot/facts.jinja2"
FACTS_MENU_TEXT = "Choose an avatar to view stored facts:"


async def _render_facts(
    avatar: AvatarDTO,
    facts_page: PageDTO[MemoryFactDTO],
) -> str:
    return await Renderer.render(
        FACTS_TEMPLATE,
        avatar=avatar,
        facts_page=facts_page,
    )


async def show_facts_menu(
    message: Message,
    user_service: UserService,
) -> None:
    avatars = await user_service.list_available_avatars()
    if not avatars:
        await message.answer(
            "No avatars are available yet.",
        )
        return

    await message.answer(
        FACTS_MENU_TEXT,
        reply_markup=build_facts_avatars_keyboard(avatars=avatars),
    )


async def edit_facts_menu(
    message: Message,
    user_service: UserService,
) -> None:
    avatars = await user_service.list_available_avatars()
    if not avatars:
        await message.edit_text("No avatars are available yet.")
        return

    await message.edit_text(
        FACTS_MENU_TEXT,
        reply_markup=build_facts_avatars_keyboard(avatars=avatars),
    )


async def _show_avatar_facts(
    message: Message,
    current_user: UserDTO,
    chat_service: ChatService,
    avatar_id: UUID,
    page: int = 1,
) -> None:
    avatar, facts_page = await chat_service.get_avatar_facts(
        current_user=current_user,
        avatar_id=avatar_id,
        page=page,
        page_size=FACTS_PAGE_SIZE,
    )
    await message.answer(
        await _render_facts(
            avatar=avatar,
            facts_page=facts_page,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=build_facts_pagination_keyboard(
            avatar_id=avatar.id,
            facts_page=facts_page,
        ),
    )


async def _edit_avatar_facts(
    message: Message,
    current_user: UserDTO,
    chat_service: ChatService,
    avatar_id: UUID,
    page: int = 1,
) -> None:
    avatar, facts_page = await chat_service.get_avatar_facts(
        current_user=current_user,
        avatar_id=avatar_id,
        page=page,
        page_size=FACTS_PAGE_SIZE,
    )
    await message.edit_text(
        await _render_facts(
            avatar=avatar,
            facts_page=facts_page,
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=build_facts_pagination_keyboard(
            avatar_id=avatar.id,
            facts_page=facts_page,
        ),
    )


@router.message(
    UserState.chatting,
    Command("facts"),
)
async def facts(
    message: Message,
    user_service: UserService,
) -> None:
    await show_facts_menu(
        message=message,
        user_service=user_service,
    )


@router.callback_query(F.data == FACTS_MENU_CALLBACK)
async def facts_menu(
    callback_query: CallbackQuery,
    user_service: UserService,
) -> None:
    await callback_query.answer()
    message = callback_query.message
    if message is None:
        return

    await edit_facts_menu(
        message=message,
        user_service=user_service,
    )


@router.callback_query(
    F.data.startswith(FACTS_AVATAR_CALLBACK_PREFIX),
)
async def facts_avatar(
    callback_query: CallbackQuery,
    current_user: UserDTO,
    chat_service: ChatService,
) -> None:
    avatar_id = parse_facts_avatar_callback_data(callback_query.data)
    if avatar_id is None:
        await callback_query.answer(
            "Invalid avatar selection.",
            show_alert=True,
        )
        return

    message = callback_query.message
    if message is None:
        await callback_query.answer()
        return

    try:
        await _edit_avatar_facts(
            message=message,
            current_user=current_user,
            chat_service=chat_service,
            avatar_id=avatar_id,
            page=1,
        )
        await callback_query.answer()
    except AvatarNotFound:
        await callback_query.answer(
            "Selected avatar does not exist.",
            show_alert=True,
        )


@router.callback_query(
    F.data.startswith(FACTS_PAGE_CALLBACK_PREFIX),
)
async def facts_page(
    callback_query: CallbackQuery,
    current_user: UserDTO,
    chat_service: ChatService,
) -> None:
    page_payload = parse_facts_page_callback_data(callback_query.data)
    if page_payload is None:
        await callback_query.answer(
            "Invalid facts page.",
            show_alert=True,
        )
        return

    message = callback_query.message
    if message is None:
        await callback_query.answer()
        return

    avatar_id, page = page_payload
    try:
        await _edit_avatar_facts(
            message=message,
            current_user=current_user,
            chat_service=chat_service,
            avatar_id=avatar_id,
            page=page,
        )
        await callback_query.answer()
    except AvatarNotFound:
        await callback_query.answer(
            "Selected avatar does not exist.",
            show_alert=True,
        )
