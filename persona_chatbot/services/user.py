from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.common.exceptions import UserNotFound
from persona_chatbot.db.repos.user import UserRepo
from persona_chatbot.dto.user import UserCreateDTO
from persona_chatbot.dto.user import UserDTO


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._user_repo = UserRepo(session=session)

    async def get_or_create(
        self,
        telegram_user_id: int,
    ) -> UserDTO:
        try:
            return await self._user_repo.get(
                telegram_user_id=telegram_user_id,
            )
        except UserNotFound:
            return await self._user_repo.create(
                dto=UserCreateDTO(
                    telegram_user_id=telegram_user_id,
                ),
            )
