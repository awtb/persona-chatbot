from fastapi import Request

from persona_chatbot.settings import ApiSettings


def get_settings(
    request: Request,
) -> ApiSettings:
    return request.app.state.settings
