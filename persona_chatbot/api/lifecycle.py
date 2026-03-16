import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from aiogram import Bot
from fastapi import FastAPI
from faststream.redis import RedisBroker

from persona_chatbot.bot.app import build_bot_commands
from persona_chatbot.settings import ApiSettings

logger = structlog.get_logger(__name__)


async def setup_telegram_updates_broker(app_instance: FastAPI) -> None:
    settings: ApiSettings = app_instance.state.settings
    broker = RedisBroker(settings.redis_url)
    await broker.connect()
    app_instance.state.tg_updates_broker = broker


def build_telegram_bot(settings: ApiSettings) -> Bot:
    return Bot(
        token=settings.tg_bot_token,
    )


async def setup_telegram_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        commands=build_bot_commands(),
    )


async def setup_telegram_webhook(bot: Bot, settings: ApiSettings) -> None:
    attempt_n = 1

    while attempt_n <= 3:
        logger.info("Setting up telegram-bot webhook, attempt %d", attempt_n)

        try:
            await bot.set_webhook(
                url=settings.tg_bot_webhook_url,
                secret_token=settings.tg_bot_webhook_token,
            )
        except Exception as e:
            logger.exception(
                "Failed to set webhook, waiting for %d seconds",
                attempt_n * 5,
                exc_info=e,
            )
            await asyncio.sleep(attempt_n * 5)
        else:
            logger.info("Webhook is up to date.")
            return

        attempt_n += 1

    logger.error("Failed to set webhook.")

    raise RuntimeError


async def sync_telegram_bot(settings: ApiSettings) -> None:
    bot = build_telegram_bot(settings)
    try:
        await setup_telegram_commands(bot)
        await setup_telegram_webhook(bot, settings)
    finally:
        await bot.session.close()


async def remove_telegram_updates_broker(app_instance: FastAPI) -> None:
    await app_instance.state.tg_updates_broker.close()


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator:
    await setup_telegram_updates_broker(app_instance)
    await sync_telegram_bot(app_instance.state.settings)
    yield
    await remove_telegram_updates_broker(app_instance)
