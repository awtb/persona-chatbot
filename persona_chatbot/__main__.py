from enum import StrEnum

import uvicorn
from typer import Argument
from typer import Option
from typer import Typer

from persona_chatbot.logging import build_logging_config
from persona_chatbot.settings import get_api_settings
from persona_chatbot.settings import get_worker_settings
from persona_chatbot.settings import RuntimeSettings

app = Typer()


class AppComponent(StrEnum):
    API = "api"
    WORKER = "worker"


def _run_component(
    component: AppComponent,
    settings: RuntimeSettings,
    reload: bool,
) -> None:
    app_path = "persona_chatbot.api.app:build_app"

    if component is AppComponent.WORKER:
        app_path = "persona_chatbot.worker.app:build_asgi_app"

    uvicorn.run(
        app_path,
        factory=True,
        reload=reload,
        host=settings.host,
        port=settings.port,
        workers=settings.processes_count,
        log_config=build_logging_config(settings),
        access_log=False,
    )


@app.command("start")
def start_app(
    component: AppComponent = Argument(...),
    reload: bool = Option(
        default=False,
    ),
) -> None:
    if component is AppComponent.API:
        settings: RuntimeSettings = get_api_settings()
    else:
        settings = get_worker_settings()
    _run_component(
        component=component,
        settings=settings,
        reload=reload,
    )


app()
