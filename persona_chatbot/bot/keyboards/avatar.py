from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from persona_chatbot.bot.callbacks import AVATAR_BACK_CALLBACK
from persona_chatbot.bot.callbacks import build_avatar_preview_callback_data
from persona_chatbot.bot.callbacks import build_avatar_select_callback_data
from persona_chatbot.dto.avatar import AvatarDTO


def build_avatar_keyboard(
    avatars: list[AvatarDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for avatar in avatars:
        builder.button(
            text=f"🎭 {avatar.name}",
            callback_data=build_avatar_preview_callback_data(
                avatar_id=avatar.id,
            ),
        )

    builder.adjust(1)
    return builder.as_markup()


def build_avatar_preview_keyboard(
    avatar: AvatarDTO,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"🎭 Select {avatar.name}",
        callback_data=build_avatar_select_callback_data(
            avatar_id=avatar.id,
        ),
    )
    builder.button(
        text="Back",
        callback_data=AVATAR_BACK_CALLBACK,
    )
    builder.adjust(1, 1)
    return builder.as_markup()
