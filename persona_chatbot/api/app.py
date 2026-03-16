from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from persona_chatbot.api.lifecycle import lifespan
from persona_chatbot.api.routers.internal import router as internal_router
from persona_chatbot.api.routers.telegram import router as telegram_router
from persona_chatbot.logging import configure_logging
from persona_chatbot.logging.middleware import RequestLoggingMiddleware
from persona_chatbot.settings import ApiSettings
from persona_chatbot.settings import get_api_settings


def setup_middlewares(app_instance: FastAPI, settings: ApiSettings) -> None:
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
    app_instance.include_router(internal_router)
    app_instance.include_router(telegram_router)


def build_app() -> FastAPI:
    settings = get_api_settings()
    configure_logging(settings)

    app = FastAPI(
        title="Persona Chatbot API",
        version="1.0",
        description="Persona Chatbot API",
        lifespan=lifespan,
    )
    app.state.settings = settings

    setup_middlewares(app, settings)
    setup_routers(app)

    return app
