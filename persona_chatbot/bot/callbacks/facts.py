from uuid import UUID

FACTS_MENU_CALLBACK = "facts:menu"
FACTS_AVATAR_CALLBACK_PREFIX = "facts:avatar:"
FACTS_PAGE_CALLBACK_PREFIX = "facts:page:"


def build_facts_avatar_callback_data(
    avatar_id: UUID,
) -> str:
    return f"{FACTS_AVATAR_CALLBACK_PREFIX}{avatar_id}"


def parse_facts_avatar_callback_data(
    callback_data: str | None,
) -> UUID | None:
    if callback_data is None:
        return None
    if not callback_data.startswith(FACTS_AVATAR_CALLBACK_PREFIX):
        return None

    prefix_length = len(FACTS_AVATAR_CALLBACK_PREFIX)
    avatar_id_text = callback_data[prefix_length:]
    try:
        return UUID(avatar_id_text)
    except ValueError:
        return None


def build_facts_page_callback_data(
    *,
    avatar_id: UUID,
    page: int,
) -> str:
    return f"{FACTS_PAGE_CALLBACK_PREFIX}{avatar_id}:{page}"


def parse_facts_page_callback_data(
    callback_data: str | None,
) -> tuple[UUID, int] | None:
    if callback_data is None:
        return None
    if not callback_data.startswith(FACTS_PAGE_CALLBACK_PREFIX):
        return None

    prefix_length = len(FACTS_PAGE_CALLBACK_PREFIX)
    payload = callback_data[prefix_length:]
    avatar_id_text, separator, page_text = payload.partition(":")
    if separator != ":" or not page_text.isdigit():
        return None

    try:
        avatar_id = UUID(avatar_id_text)
    except ValueError:
        return None

    page = int(page_text)
    if page < 1:
        return None

    return avatar_id, page
