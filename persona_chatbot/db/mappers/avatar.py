from persona_chatbot.db.models.avatar import Avatar
from persona_chatbot.dto.avatar import AvatarDTO


def to_avatar_dto(avatar: Avatar) -> AvatarDTO:
    return AvatarDTO(
        id=avatar.id,
        name=avatar.name,
        system_prompt=avatar.system_prompt,
        created_at=avatar.created_at,
    )
