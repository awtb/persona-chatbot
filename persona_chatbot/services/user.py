from sqlalchemy.ext.asyncio import AsyncSession

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
        user = await self._user_repo.get(
            telegram_user_id=telegram_user_id,
        )
        if user is not None:
            return user

        try:
            return await self._user_repo.create(
                dto=UserCreateDTO(
                    telegram_user_id=telegram_user_id,
                ),
            )
        except Exception as exc:
            user = await self._user_repo.get(
                telegram_user_id=telegram_user_id,
            )
            if user is not None:
                return user

            msg = (
                "Failed to resolve current user "
                f"for telegram_user_id={telegram_user_id}"
            )
            raise RuntimeError(msg) from exc
