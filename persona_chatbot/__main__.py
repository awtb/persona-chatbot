import uvicorn
from typer import Option
from typer import Typer

from persona_chatbot.logging import build_logging_config
from persona_chatbot.settings import get_settings

app = Typer()


@app.command("start")
def start_app(
    reload: bool = Option(
        default=False,
    ),
) -> None:
    settings = get_settings()
    log_config = build_logging_config(settings)

    uvicorn.run(
        "persona_chatbot.api.app:build_app",
        reload=reload,
        workers=settings.serving_workers_count,
        factory=True,
        host=settings.serving_host,
        port=settings.serving_port,
        log_config=log_config,
        access_log=False,
    )


app()
