from fastapi import APIRouter

router = APIRouter(tags=["Telegram"])


@router.post("/")
async def proces_telegram_update():
    raise NotImplementedError
