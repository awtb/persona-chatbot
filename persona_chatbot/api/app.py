from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from persona_chatbot.logging.config import build_logging_config
from persona_chatbot.logging.middleware import RequestLoggingMiddleware
from persona_chatbot.settings import get_settings
from persona_chatbot.settings import Settings


def load_settings(app_instance: FastAPI) -> Settings:
    settings = get_settings()
    build_logging_config(settings)
    app_instance.state.settings = settings

    return settings


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
    raise NotImplementedError


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
