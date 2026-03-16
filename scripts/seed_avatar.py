import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_NAME = "Test Avatar"
DEFAULT_PROMPT = " ".join(
    [
        "You are a helpful test assistant.",
        "Keep responses short and clear.",
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed a basic avatar for local testing.",
    )
    parser.add_argument(
        "--name",
        default=DEFAULT_NAME,
        help=f"Avatar name (default: {DEFAULT_NAME!r}).",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Avatar system prompt.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Update prompt if avatar with this name already exists.",
    )
    return parser.parse_args()


async def seed_avatar(
    name: str,
    prompt: str,
    overwrite: bool,
) -> None:
    from persona_chatbot.db.models.avatar import Avatar
    from persona_chatbot.db.session import build_session_maker
    from persona_chatbot.settings import get_worker_settings

    settings = get_worker_settings()
    db_url = URL.create(
        drivername=settings.db_driver,
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_async_engine(db_url)
    session_maker = build_session_maker(engine=engine)

    try:
        async with session_maker() as session:
            avatar = await session.scalar(
                select(Avatar).where(Avatar.name == name),
            )
            if avatar is None:
                avatar = Avatar(
                    name=name,
                    system_prompt=prompt,
                )
                session.add(avatar)
                await session.commit()
                await session.refresh(avatar)
                print(
                    f"Created avatar id={avatar.id} name={avatar.name!r}",
                )
                return

            if overwrite:
                avatar.system_prompt = prompt
                await session.commit()
                print(
                    f"Updated avatar id={avatar.id} name={avatar.name!r}",
                )
                return

            print(
                "Avatar already exists "
                f"(id={avatar.id}, name={avatar.name!r}). "
                "Use --overwrite to update prompt.",
            )
    finally:
        await engine.dispose()


def main() -> None:
    args = parse_args()
    asyncio.run(
        seed_avatar(
            name=args.name,
            prompt=args.prompt,
            overwrite=args.overwrite,
        ),
    )


if __name__ == "__main__":
    main()
