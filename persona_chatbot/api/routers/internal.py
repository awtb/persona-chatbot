from aiogram import Dispatcher
from fastapi import Request
from jinja2 import Environment
from sqlalchemy.ext.asyncio import async_sessionmaker

from persona_chatbot.settings import Settings


def get_env(
    request: Request,
) -> Environment:
    return request.app.state.env


def get_dispatcher(
    env: Environment, session_maker: async_sessionmaker, settings: Settings
) -> Dispatcher:
    dp = Dispatcher(
        env=env,
        settings=settings,
    )

    return dp
