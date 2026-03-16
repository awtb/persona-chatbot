from pathlib import Path
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined

TEMPLATES_DIR = Path(__file__).resolve().parent


class Renderer:
    _env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        undefined=StrictUndefined,
        autoescape=False,
        enable_async=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    @classmethod
    async def render(
        cls,
        template_name: str,
        **context: Any,
    ) -> str:
        template = cls._env.get_template(template_name)
        return (await template.render_async(**context)).strip()
