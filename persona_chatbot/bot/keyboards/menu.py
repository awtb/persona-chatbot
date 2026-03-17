from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from persona_chatbot.bot.callbacks import MENU_AVATARS_CALLBACK
from persona_chatbot.bot.callbacks import MENU_HISTORY_CALLBACK
from persona_chatbot.bot.callbacks import MENU_RESET_CALLBACK


def build_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📜 History",
        callback_data=MENU_HISTORY_CALLBACK,
    )
    builder.button(
        text="🎭 Avatars",
        callback_data=MENU_AVATARS_CALLBACK,
    )
    builder.button(
        text="♻️ Reset",
        callback_data=MENU_RESET_CALLBACK,
    )
    builder.adjust(2, 1)
    return builder.as_markup()
