from uuid import UUID

AVATAR_PREVIEW_CALLBACK_PREFIX = "avatar_preview:"
AVATAR_SELECT_CALLBACK_PREFIX = "avatar_select:"
AVATAR_BACK_CALLBACK = "avatar_back"


def _build_avatar_callback_data(
    prefix: str,
    avatar_id: UUID,
) -> str:
    return f"{prefix}{avatar_id}"


def _parse_avatar_callback_data(
    callback_data: str | None,
    prefix: str,
) -> UUID | None:
    if callback_data is None:
        return None
    if not callback_data.startswith(prefix):
        return None

    prefix_length = len(prefix)
    avatar_id_str = callback_data[prefix_length:]
    try:
        return UUID(avatar_id_str)
    except ValueError:
        return None


def build_avatar_preview_callback_data(
    avatar_id: UUID,
) -> str:
    return _build_avatar_callback_data(
        AVATAR_PREVIEW_CALLBACK_PREFIX,
        avatar_id,
    )


def build_avatar_select_callback_data(
    avatar_id: UUID,
) -> str:
    return _build_avatar_callback_data(
        AVATAR_SELECT_CALLBACK_PREFIX,
        avatar_id,
    )


def parse_avatar_preview_callback_data(
    callback_data: str | None,
) -> UUID | None:
    return _parse_avatar_callback_data(
        callback_data,
        AVATAR_PREVIEW_CALLBACK_PREFIX,
    )


def parse_avatar_select_callback_data(
    callback_data: str | None,
) -> UUID | None:
    return _parse_avatar_callback_data(
        callback_data,
        AVATAR_SELECT_CALLBACK_PREFIX,
    )
