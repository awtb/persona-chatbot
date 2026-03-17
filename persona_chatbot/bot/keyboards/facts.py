from uuid import UUID

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from persona_chatbot.bot.callbacks import build_facts_avatar_callback_data
from persona_chatbot.bot.callbacks import build_facts_page_callback_data
from persona_chatbot.bot.callbacks import FACTS_MENU_CALLBACK
from persona_chatbot.dto.avatar import AvatarDTO
from persona_chatbot.dto.base import PageDTO
from persona_chatbot.dto.memory import MemoryFactDTO


def build_facts_avatars_keyboard(
    avatars: list[AvatarDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for avatar in avatars:
        builder.button(
            text=f"🎭 {avatar.name}",
            callback_data=build_facts_avatar_callback_data(
                avatar_id=avatar.id,
            ),
        )

    builder.adjust(1)
    return builder.as_markup()


def build_facts_pagination_keyboard(
    *,
    avatar_id: UUID,
    facts_page: PageDTO[MemoryFactDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if facts_page.page > 1:
        builder.button(
            text="← Previous",
            callback_data=build_facts_page_callback_data(
                avatar_id=avatar_id,
                page=facts_page.page - 1,
            ),
        )

    builder.button(
        text="🎭 Avatars",
        callback_data=FACTS_MENU_CALLBACK,
    )

    if facts_page.page < facts_page.total_pages:
        builder.button(
            text="Next →",
            callback_data=build_facts_page_callback_data(
                avatar_id=avatar_id,
                page=facts_page.page + 1,
            ),
        )

    builder.adjust(3)
    return builder.as_markup()
