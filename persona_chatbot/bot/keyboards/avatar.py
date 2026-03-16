from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from persona_chatbot.bot.callbacks import build_avatar_select_callback_data
from persona_chatbot.dto.avatar import AvatarDTO


def build_avatar_keyboard(
    avatars: list[AvatarDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for avatar in avatars:
        builder.button(
            text=avatar.name,
            callback_data=build_avatar_select_callback_data(
                avatar_id=avatar.id,
            ),
        )

    builder.adjust(1)
    return builder.as_markup()
