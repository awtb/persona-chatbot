from fastapi import APIRouter

router = APIRouter(
    tags=["Internal"],
    prefix="/internal",
)


@router.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
