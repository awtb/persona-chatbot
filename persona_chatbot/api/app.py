import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from aiogram import Bot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from persona_chatbot.api.routers.telegram import router as telegram_router
from persona_chatbot.bot.app import build_dispatcher
from persona_chatbot.logging.config import build_logging_config
from persona_chatbot.logging.middleware import RequestLoggingMiddleware
from persona_chatbot.settings import get_settings
from persona_chatbot.settings import Settings

logger = structlog.get_logger(__name__)


def load_settings(app_instance: FastAPI) -> Settings:
    settings = get_settings()
    build_logging_config(settings)
    app_instance.state.settings = settings

    return settings


def setup_telegram_dispatcher(app_instance: FastAPI) -> None:
    app_instance.state.tg_dispatcher = build_dispatcher()


def setup_telegram_bot(app_instance: FastAPI) -> None:
    app_instance.state.tg_bot = Bot(
        token=app_instance.state.settings.tg_bot_token,
    )


async def setup_telegram_webhook(app_instance: FastAPI) -> None:
    attempt_n = 1
    bot: Bot = app_instance.state.tg_bot
    settings: Settings = app_instance.state.settings

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


async def setup_db_engine(app_instance: FastAPI) -> None:
    settings: Settings = app_instance.state.settings

    uri = URL.create(
        drivername=settings.db_driver,
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_async_engine(uri)

    app_instance.state.engine = engine


async def remove_engine(app_instance: FastAPI) -> None:
    await app_instance.state.engine.dispose()


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator:
    load_settings(app_instance)
    setup_telegram_dispatcher(app_instance)
    setup_telegram_bot(app_instance)
    await setup_telegram_webhook(app_instance)
    await setup_db_engine(app_instance)
    yield
    await remove_engine(app_instance)


def setup_middlewares(app_instance: FastAPI) -> None:
    settings: Settings = load_settings(app_instance)

    app_instance.add_middleware(
        RequestLoggingMiddleware,
    )
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        allow_credentials=settings.cors_allow_credentials,
    )


def setup_routers(app_instance: FastAPI) -> None:
    app_instance.include_router(telegram_router)


def build_app() -> FastAPI:
    app = FastAPI(
        title="Persona Chatbot API",
        version="1.0",
        description="Persona Chatbot API",
        lifespan=lifespan,
    )

    setup_middlewares(app)
    setup_routers(app)

    return app
