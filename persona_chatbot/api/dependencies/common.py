from fastapi import Request

from persona_chatbot.settings import Settings


def get_settings(
    request: Request,
) -> Settings:
    return request.app.state.settings
