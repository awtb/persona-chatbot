from aiogram import Bot
from faststream.redis import RedisBroker
from redis.asyncio import Redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from persona_chatbot.bot.app import build_dispatcher
from persona_chatbot.db.session import build_session_maker
from persona_chatbot.settings import WorkerSettings

BOT_CONTEXT_KEY = "telegram_worker_bot"
DISPATCHER_CONTEXT_KEY = "telegram_worker_dispatcher"
ENGINE_CONTEXT_KEY = "telegram_worker_engine"


async def startup_worker(
    *,
    broker: RedisBroker,
    settings: WorkerSettings,
) -> None:
    db_url = URL.create(
        drivername=settings.db_driver,
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_async_engine(db_url)
    session_maker: async_sessionmaker[AsyncSession] = build_session_maker(
        engine=engine,
    )
    redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
    )
    dispatcher = build_dispatcher(
        session_maker=session_maker,
        settings=settings,
        redis=redis,
    )
    bot = Bot(token=settings.tg_bot_token)
    broker.context.set_global(BOT_CONTEXT_KEY, bot)
    broker.context.set_global(DISPATCHER_CONTEXT_KEY, dispatcher)
    broker.context.set_global(ENGINE_CONTEXT_KEY, engine)


async def shutdown_worker(
    *,
    broker: RedisBroker,
) -> None:
    bot = broker.context.get(BOT_CONTEXT_KEY)
    dispatcher = broker.context.get(DISPATCHER_CONTEXT_KEY)
    engine = broker.context.get(ENGINE_CONTEXT_KEY)

    if bot is None or dispatcher is None or engine is None:
        return

    await dispatcher.storage.close()
    await bot.session.close()
    await engine.dispose()
    broker.context.reset_global(BOT_CONTEXT_KEY)
    broker.context.reset_global(DISPATCHER_CONTEXT_KEY)
    broker.context.reset_global(ENGINE_CONTEXT_KEY)
