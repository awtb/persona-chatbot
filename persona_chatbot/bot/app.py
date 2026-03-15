from aiogram import Dispatcher

from persona_chatbot.bot.routers.onboarding import router as onboarding_router


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.include_router(
        onboarding_router,
    )

    return dp
