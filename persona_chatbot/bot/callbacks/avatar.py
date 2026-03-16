from uuid import UUID

AVATAR_SELECT_CALLBACK_PREFIX = "avatar_select:"


def build_avatar_select_callback_data(
    avatar_id: UUID,
) -> str:
    return f"{AVATAR_SELECT_CALLBACK_PREFIX}{avatar_id}"


def parse_avatar_select_callback_data(
    callback_data: str | None,
) -> UUID | None:
    if callback_data is None:
        return None
    if not callback_data.startswith(AVATAR_SELECT_CALLBACK_PREFIX):
        return None

    prefix_length = len(AVATAR_SELECT_CALLBACK_PREFIX)
    avatar_id_str = callback_data[prefix_length:]
    try:
        return UUID(avatar_id_str)
    except ValueError:
        return None
