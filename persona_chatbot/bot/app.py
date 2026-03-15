from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.bot.middlewares import CurrentUserProviderMiddleware
from persona_chatbot.bot.middlewares import SessionProviderMiddleware
from persona_chatbot.bot.middlewares import UserDependenciesMiddleware
from persona_chatbot.bot.routers.onboarding import router as onboarding_router


def build_dispatcher(
    session_maker: async_sessionmaker[AsyncSession],
) -> Dispatcher:
    dp = Dispatcher()
    dp.update.outer_middleware(
        SessionProviderMiddleware(session_maker=session_maker),
    )
    dp.update.outer_middleware(
        UserDependenciesMiddleware(),
    )
    dp.update.outer_middleware(
        CurrentUserProviderMiddleware(),
    )

    dp.include_router(
        onboarding_router,
    )

    return dp
