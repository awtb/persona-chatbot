from aiogram import Bot
from faststream.redis import RedisBroker
from redis.asyncio import Redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from persona_chatbot.bot.app import build_dispatcher
from persona_chatbot.db.session import build_session_maker
from persona_chatbot.llm.client import LLMClient
from persona_chatbot.settings import WorkerSettings

BOT_CONTEXT_KEY = "telegram_worker_bot"
DISPATCHER_CONTEXT_KEY = "telegram_worker_dispatcher"
ENGINE_CONTEXT_KEY = "telegram_worker_engine"
SESSION_MAKER_CONTEXT_KEY = "telegram_worker_session_maker"
LLM_CLIENT_CONTEXT_KEY = "telegram_worker_llm_client"


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
        broker=broker,
    )
    bot = Bot(token=settings.tg_bot_token)
    llm_client = LLMClient(
        api_key=settings.llm_provider_api_key,
        base_url=settings.llm_provider_base_url,
        model=settings.llm_model,
        timeout_sec=settings.llm_timeout_sec,
    )
    broker.context.set_global(BOT_CONTEXT_KEY, bot)
    broker.context.set_global(DISPATCHER_CONTEXT_KEY, dispatcher)
    broker.context.set_global(ENGINE_CONTEXT_KEY, engine)
    broker.context.set_global(SESSION_MAKER_CONTEXT_KEY, session_maker)
    broker.context.set_global(LLM_CLIENT_CONTEXT_KEY, llm_client)


async def shutdown_worker(
    *,
    broker: RedisBroker,
) -> None:
    bot = broker.context.get(BOT_CONTEXT_KEY)
    dispatcher = broker.context.get(DISPATCHER_CONTEXT_KEY)
    engine = broker.context.get(ENGINE_CONTEXT_KEY)
    session_maker = broker.context.get(SESSION_MAKER_CONTEXT_KEY)
    llm_client = broker.context.get(LLM_CLIENT_CONTEXT_KEY)
    context_values = (
        bot,
        dispatcher,
        engine,
        session_maker,
        llm_client,
    )

    if any(value is None for value in context_values):
        return

    await dispatcher.storage.close()
    await bot.session.close()
    await engine.dispose()
    broker.context.reset_global(BOT_CONTEXT_KEY)
    broker.context.reset_global(DISPATCHER_CONTEXT_KEY)
    broker.context.reset_global(ENGINE_CONTEXT_KEY)
    broker.context.reset_global(SESSION_MAKER_CONTEXT_KEY)
    broker.context.reset_global(LLM_CLIENT_CONTEXT_KEY)
