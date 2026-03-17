from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from faststream.redis import RedisBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.bot.middlewares import AvatarDependenciesMiddleware
from persona_chatbot.bot.middlewares import ChatDependenciesMiddleware
from persona_chatbot.bot.middlewares import ChatProcessingMiddleware
from persona_chatbot.bot.middlewares import CurrentUserProviderMiddleware
from persona_chatbot.bot.middlewares import SessionProviderMiddleware
from persona_chatbot.bot.middlewares import SettingsProviderMiddleware
from persona_chatbot.bot.middlewares import UserDependenciesMiddleware
from persona_chatbot.bot.routers.avatar import router as avatar_router
from persona_chatbot.bot.routers.chat import router as chat_router
from persona_chatbot.bot.routers.facts import router as facts_router
from persona_chatbot.bot.routers.history import router as history_router
from persona_chatbot.bot.routers.menu import router as menu_router
from persona_chatbot.bot.routers.onboarding import router as onboarding_router
from persona_chatbot.bot.routers.reset import router as reset_router
from persona_chatbot.settings import WorkerSettings


def build_bot_commands() -> list[BotCommand]:
    return [
        BotCommand(
            command="start",
            description="Open the welcome screen",
        ),
        BotCommand(
            command="menu",
            description="Open quick actions",
        ),
        BotCommand(
            command="avatars",
            description="Choose an avatar",
        ),
        BotCommand(
            command="history",
            description="Show the last 10 messages",
        ),
        BotCommand(
            command="facts",
            description="Browse stored facts by avatar",
        ),
        BotCommand(
            command="reset",
            description="Start a fresh chat",
        ),
    ]


def build_dispatcher(
    session_maker: async_sessionmaker[AsyncSession],
    settings: WorkerSettings,
    redis: Redis,
    broker: RedisBroker,
) -> Dispatcher:
    dp = Dispatcher(
        storage=RedisStorage(redis=redis),
    )
    dp.update.outer_middleware(
        SessionProviderMiddleware(session_maker=session_maker),
    )
    dp.update.outer_middleware(
        SettingsProviderMiddleware(settings=settings),
    )
    dp.update.outer_middleware(
        UserDependenciesMiddleware(),
    )
    dp.update.outer_middleware(
        AvatarDependenciesMiddleware(),
    )
    dp.update.outer_middleware(
        ChatDependenciesMiddleware(broker=broker),
    )
    dp.update.outer_middleware(
        CurrentUserProviderMiddleware(),
    )
    dp.message.outer_middleware(
        ChatProcessingMiddleware(redis=redis),
    )

    dp.include_router(
        onboarding_router,
    )
    dp.include_router(
        avatar_router,
    )
    dp.include_router(
        menu_router,
    )
    dp.include_router(
        history_router,
    )
    dp.include_router(
        facts_router,
    )
    dp.include_router(
        reset_router,
    )
    dp.include_router(
        chat_router,
    )

    return dp
