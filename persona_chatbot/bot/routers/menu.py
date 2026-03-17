from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from persona_chatbot.bot.callbacks import MENU_AVATARS_CALLBACK
from persona_chatbot.bot.callbacks import MENU_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import MENU_FACTS_CALLBACK
from persona_chatbot.bot.callbacks import MENU_HISTORY_CALLBACK
from persona_chatbot.bot.callbacks import MENU_RESET_CALLBACK
from persona_chatbot.bot.keyboards import build_menu_keyboard
from persona_chatbot.bot.routers.avatar import show_avatar_selection
from persona_chatbot.bot.routers.facts import show_facts_menu
from persona_chatbot.bot.routers.history import show_history
from persona_chatbot.bot.routers.reset import perform_reset
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.chat import ChatService
from persona_chatbot.services.user import UserService

router = Router(name=__name__)


@router.message(Command("menu"))
async def menu(
    message: Message,
) -> None:
    await message.answer(
        "Menu:",
        reply_markup=build_menu_keyboard(),
    )


@router.callback_query(F.data.startswith(MENU_CALLBACK_PREFIX))
async def handle_menu_action(
    callback_query: CallbackQuery,
    current_user: UserDTO,
    user_service: UserService,
    chat_service: ChatService,
    state: FSMContext,
) -> None:
    await callback_query.answer()
    message = callback_query.message
    if message is None:
        return

    if callback_query.data == MENU_HISTORY_CALLBACK:
        await show_history(
            message=message,
            current_user=current_user,
            chat_service=chat_service,
        )
        return

    if callback_query.data == MENU_FACTS_CALLBACK:
        await show_facts_menu(
            message=message,
            user_service=user_service,
        )
        return

    if callback_query.data == MENU_AVATARS_CALLBACK:
        await show_avatar_selection(
            message=message,
            user_service=user_service,
            state=state,
        )
        return

    if callback_query.data == MENU_RESET_CALLBACK:
        await perform_reset(
            message=message,
            current_user=current_user,
            user_service=user_service,
        )
