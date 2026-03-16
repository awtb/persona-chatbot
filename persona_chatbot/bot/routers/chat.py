from collections.abc import AsyncIterable

from aiogram import F
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from persona_chatbot.bot.states import UserState
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.chat import ChatService
from persona_chatbot.services.user import UserService

router = Router(name=__name__)

STREAM_PLACEHOLDER_TEXT = "..."
TELEGRAM_MAX_TEXT_LEN = 4096


def _is_markdown_parse_error(
    error: TelegramBadRequest,
) -> bool:
    error_text = str(error).lower()
    return "can't parse entities" in error_text


def _fit_for_telegram(
    text: str,
) -> str:
    if not text:
        return STREAM_PLACEHOLDER_TEXT
    if len(text) <= TELEGRAM_MAX_TEXT_LEN:
        return text

    return f"{text[: TELEGRAM_MAX_TEXT_LEN - 3]}..."


async def _safe_edit_message(
    message: Message,
    text: str,
) -> str:
    normalized = _fit_for_telegram(text=text)
    try:
        await message.answer(
            normalized,
            parse_mode=ParseMode.MARKDOWN,
        )
    except TelegramBadRequest as e:
        if not _is_markdown_parse_error(e):
            raise
        await message.answer(normalized)

    return normalized


async def _send_message_draft(
    message: Message,
    draft_id: int,
    text: str,
) -> str:
    normalized = _fit_for_telegram(text=text)
    if normalized == STREAM_PLACEHOLDER_TEXT:
        return normalized

    try:
        await message.bot.send_message_draft(
            chat_id=message.chat.id,
            draft_id=draft_id,
            text=normalized,
            message_thread_id=message.message_thread_id,
        )
    except Exception:
        return normalized

    return normalized


async def _stream_chat_reply(
    message: Message,
    draft_id: int,
    stream: AsyncIterable[str],
) -> str:
    current_text = ""

    async for chunk in stream:
        if not chunk:
            continue

        current_text += chunk
        await _send_message_draft(
            message=message,
            draft_id=draft_id,
            text=current_text,
        )

    return current_text.strip()


@router.message(
    UserState.chatting,
    Command("reset"),
)
async def reset_chat_context(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
) -> None:
    updated_user = await user_service.reset_chat_context(
        current_user=current_user,
    )
    current_user.active_chat_id = updated_user.active_chat_id
    await message.answer(
        "Context cleared. Started a new chat with the current avatar.",
    )


@router.message(
    UserState.chatting,
    F.text,
    ~F.text.startswith("/"),
)
async def chat_with_llm(
    message: Message,
    current_user: UserDTO,
    chat_service: ChatService,
) -> None:
    if message.text is None:
        return

    draft_id = message.message_id
    stream = chat_service.stream_reply_to_message(
        current_user=current_user,
        message=message.text,
    )
    final_text = await _stream_chat_reply(
        message=message,
        draft_id=draft_id,
        stream=stream,
    )
    if not final_text:
        final_text = "I could not generate a response right now."
    await _safe_edit_message(
        message=message,
        text=final_text,
    )
