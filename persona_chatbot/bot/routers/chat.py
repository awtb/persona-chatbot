from collections.abc import AsyncIterable
from time import monotonic

from aiogram import F
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from persona_chatbot.bot.states import UserState
from persona_chatbot.common.constants import FALLBACK_RESPONSE_TEXT
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.chat import ChatService

router = Router(name=__name__)

TELEGRAM_MAX_TEXT_LEN = 4096
STREAM_INITIAL_FLUSH_AFTER_SEC = 0.15
STREAM_UPDATE_INTERVAL_SEC = 0.35
STREAM_MIN_BUFFER_CHARS = 32
STREAM_FLUSH_ENDINGS = (".", "!", "?", "\n")


def _is_markdown_parse_error(
    error: TelegramBadRequest,
) -> bool:
    error_text = str(error).lower()
    return "can't parse entities" in error_text


def _fit_for_telegram(
    text: str,
) -> str:
    if len(text) <= TELEGRAM_MAX_TEXT_LEN:
        return text

    return f"{text[: TELEGRAM_MAX_TEXT_LEN - 3]}..."


async def _send_final_message(
    message: Message,
    text: str,
    *,
    reply_to_message_id: int,
) -> str:
    normalized = _fit_for_telegram(text=text)
    try:
        await message.answer(
            normalized,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=reply_to_message_id,
        )
    except TelegramBadRequest as e:
        if not _is_markdown_parse_error(e):
            raise
        await message.answer(
            normalized,
            reply_to_message_id=reply_to_message_id,
        )

    return normalized


async def _send_reply_draft(
    message: Message,
    draft_id: int,
    text: str,
) -> str | None:
    normalized = _fit_for_telegram(text=text)
    if not normalized:
        return None

    try:
        await message.bot.send_message_draft(
            chat_id=message.chat.id,
            draft_id=draft_id,
            text=normalized,
            message_thread_id=message.message_thread_id,
            parse_mode=ParseMode.MARKDOWN,
        )
    except TelegramBadRequest as e:
        if not _is_markdown_parse_error(e):
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
    except Exception:
        return normalized

    return normalized


def _should_flush_reply_draft(
    text: str,
    chars_since_flush: int,
    elapsed_since_flush: float,
    *,
    has_sent_draft: bool,
) -> bool:
    if not text:
        return False

    if text.rstrip().endswith(STREAM_FLUSH_ENDINGS):
        return True

    if chars_since_flush >= STREAM_MIN_BUFFER_CHARS:
        return True

    if has_sent_draft:
        flush_interval = STREAM_UPDATE_INTERVAL_SEC
    else:
        flush_interval = STREAM_INITIAL_FLUSH_AFTER_SEC
    return elapsed_since_flush >= flush_interval


async def _stream_reply_draft(
    message: Message,
    draft_id: int,
    stream: AsyncIterable[str],
) -> str:
    current_text = ""
    last_sent_text: str | None = None
    last_flush_at = monotonic()
    chars_since_flush = 0

    async for chunk in stream:
        if not chunk:
            continue

        current_text += chunk
        chars_since_flush += len(chunk)
        if not _should_flush_reply_draft(
            text=current_text,
            chars_since_flush=chars_since_flush,
            elapsed_since_flush=monotonic() - last_flush_at,
            has_sent_draft=last_sent_text is not None,
        ):
            continue

        normalized = _fit_for_telegram(text=current_text)
        if normalized != last_sent_text:
            sent_text = await _send_reply_draft(
                message=message,
                draft_id=draft_id,
                text=current_text,
            )
            if sent_text is not None:
                last_sent_text = sent_text
        last_flush_at = monotonic()
        chars_since_flush = 0

    normalized = _fit_for_telegram(text=current_text)
    if normalized and normalized != last_sent_text:
        await _send_reply_draft(
            message=message,
            draft_id=draft_id,
            text=current_text,
        )

    return current_text.strip()


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

    stream = chat_service.stream_reply_to_message(
        current_user=current_user,
        message=message.text,
    )
    final_text = await _stream_reply_draft(
        message=message,
        draft_id=message.message_id,
        stream=stream,
    )
    if not final_text:
        final_text = FALLBACK_RESPONSE_TEXT
    await _send_final_message(
        message=message,
        text=final_text,
        reply_to_message_id=message.message_id,
    )
