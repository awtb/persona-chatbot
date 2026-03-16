from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status
from faststream.redis import RedisBroker

from persona_chatbot.api.dependencies.telegram import (
    get_telegram_updates_broker,
)
from persona_chatbot.api.dependencies.telegram import validate_tg_request
from persona_chatbot.api.dependencies.telegram import validate_tg_webhook_token
from persona_chatbot.schemas import TelegramUpdateTaskSchema
from persona_chatbot.worker.queues import TELEGRAM_UPDATES_QUEUE

router = APIRouter(
    tags=["Telegram"],
    prefix="/telegram",
    dependencies=[
        Depends(validate_tg_request),
        Depends(
            validate_tg_webhook_token,
        ),
    ],
)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def process_telegram_update(
    update: dict,
    request: Request,
    broker: RedisBroker = Depends(get_telegram_updates_broker),
) -> None:
    payload = TelegramUpdateTaskSchema(
        request_id=request.state.request_id,
        update=update,
    )
    await broker.publish(
        payload.model_dump(mode="json"),
        list=TELEGRAM_UPDATES_QUEUE,
        correlation_id=request.state.request_id,
    )
