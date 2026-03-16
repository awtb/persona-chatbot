import structlog
from aiogram import Bot
from aiogram import Dispatcher
from faststream import Context
from faststream.redis import RedisRouter
from structlog.contextvars import bound_contextvars

from persona_chatbot.schemas import TelegramUpdateTaskSchema
from persona_chatbot.worker.lifecycle import BOT_CONTEXT_KEY
from persona_chatbot.worker.lifecycle import DISPATCHER_CONTEXT_KEY
from persona_chatbot.worker.queues import TELEGRAM_UPDATES_QUEUE

logger = structlog.get_logger(__name__)
router = RedisRouter()


async def _feed_update(
    *,
    bot: Bot,
    dispatcher: Dispatcher,
    request_id: str,
    update: dict,
) -> None:
    try:
        await dispatcher.feed_raw_update(
            bot=bot,
            update=update,
        )
    except Exception as e:
        logger.exception(
            "Failed to process telegram update",
            request_id=request_id,
            telegram_update_id=update.get("update_id"),
            exc_info=e,
        )
        raise


@router.subscriber(list=TELEGRAM_UPDATES_QUEUE)
async def process_telegram_update(
    payload: TelegramUpdateTaskSchema,
    bot: Bot = Context(BOT_CONTEXT_KEY),
    dispatcher: Dispatcher = Context(DISPATCHER_CONTEXT_KEY),
) -> None:
    with bound_contextvars(request_id=payload.request_id):
        logger.info(
            "Processing telegram update",
            request_id=payload.request_id,
        )
        await _feed_update(
            bot=bot,
            dispatcher=dispatcher,
            request_id=payload.request_id,
            update=payload.update,
        )
