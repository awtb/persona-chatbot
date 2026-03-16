from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.common.exceptions import AvatarNotSelected
from persona_chatbot.db.repos.avatar import AvatarRepo
from persona_chatbot.dto.avatar import AvatarDTO
from persona_chatbot.dto.user import UserDTO


class AvatarService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._avatar_repo = AvatarRepo(session=session)

    async def resolve_avatar(
        self,
        current_user: UserDTO,
    ) -> AvatarDTO:
        if current_user.current_avatar_id is None:
            raise AvatarNotSelected()

        return await self._avatar_repo.get(
            avatar_id=current_user.current_avatar_id,
        )

    async def resolve_avatar_prompt(
        self,
        current_user: UserDTO,
    ) -> str:
        avatar = await self.resolve_avatar(current_user=current_user)
        return avatar.system_prompt
