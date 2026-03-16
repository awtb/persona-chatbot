from faststream import FastStream
from faststream.asgi import AsgiFastStream
from faststream.asgi import make_ping_asgi
from faststream.redis import RedisBroker

from persona_chatbot.logging import configure_logging
from persona_chatbot.settings import get_worker_settings
from persona_chatbot.settings import WorkerSettings
from persona_chatbot.worker.lifecycle import shutdown_worker
from persona_chatbot.worker.lifecycle import startup_worker
from persona_chatbot.worker.tasks import router as tasks_router


def build_broker(settings: WorkerSettings) -> RedisBroker:
    broker = RedisBroker(settings.redis_url)
    broker.include_router(tasks_router)
    return broker


def build_app(
    *,
    broker: RedisBroker,
    settings: WorkerSettings,
) -> FastStream:
    async def startup() -> None:
        await startup_worker(
            broker=broker,
            settings=settings,
        )

    async def shutdown() -> None:
        await shutdown_worker(broker=broker)

    return FastStream(
        broker,
        on_startup=[startup],
        on_shutdown=[shutdown],
    )


def build_asgi_app() -> AsgiFastStream:
    settings = get_worker_settings()
    configure_logging(settings)
    broker = build_broker(settings)
    app = build_app(
        broker=broker,
        settings=settings,
    )

    return AsgiFastStream.from_app(
        app,
        asgi_routes=(("/health", make_ping_asgi(broker)),),
    )
