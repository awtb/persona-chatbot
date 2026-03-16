from uuid import UUID

from sqlalchemy import select

from persona_chatbot.common.exceptions import AvatarNotFound
from persona_chatbot.db.mappers.avatar import to_avatar_dto
from persona_chatbot.db.models.avatar import Avatar
from persona_chatbot.db.repos.base import BaseRepository
from persona_chatbot.dto.avatar import AvatarDTO


class AvatarRepo(BaseRepository):
    async def get(
        self,
        avatar_id: UUID,
    ) -> AvatarDTO:
        query = select(Avatar).where(Avatar.id == avatar_id)
        avatar = await self._session.scalar(query)
        if avatar is None:
            raise AvatarNotFound(avatar_id=avatar_id)

        return to_avatar_dto(avatar)

    async def list_all(
        self,
    ) -> list[AvatarDTO]:
        query = select(Avatar).order_by(Avatar.created_at.asc())
        avatars = (await self._session.scalars(query)).all()

        return [to_avatar_dto(avatar) for avatar in avatars]
