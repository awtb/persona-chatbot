import asyncio

import structlog
from aiogram import Bot
from aiogram import Dispatcher
from fastapi import APIRouter
from fastapi import Depends

from persona_chatbot.api.dependencies.telegram import get_telegram_bot
from persona_chatbot.api.dependencies.telegram import get_telegram_dispatcher
from persona_chatbot.api.dependencies.telegram import validate_tg_request
from persona_chatbot.api.dependencies.telegram import validate_tg_webhook_token

logger = structlog.get_logger(__name__)

router = APIRouter(
    tags=["Telegram"],
    prefix="/telegram",
    dependencies=[
        Depends(validate_tg_request),
        Depends(
            validate_tg_webhook_token,
        ),
    ],
)


async def _process_update_in_background(
    update: dict,
    bot: Bot,
    dispatcher: Dispatcher,
) -> None:
    try:
        await dispatcher.feed_raw_update(
            bot=bot,
            update=update,
        )
    except Exception as e:
        logger.exception("Failed to handle update", exc_info=e)


@router.post("")
async def proces_telegram_update(
    update: dict,
    bot: Bot = Depends(get_telegram_bot),
    dispatcher: Dispatcher = Depends(get_telegram_dispatcher),
) -> None:
    asyncio.create_task(
        _process_update_in_background(
            update=update,
            bot=bot,
            dispatcher=dispatcher,
        ),
    )
