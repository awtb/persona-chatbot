from uuid import UUID

from sqlalchemy import select

from persona_chatbot.db.mappers.user import apply_user_update_dto
from persona_chatbot.db.mappers.user import to_user_dto
from persona_chatbot.db.models.user import User
from persona_chatbot.db.repos.base import BaseRepository
from persona_chatbot.dto.user import UserCreateDTO
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.dto.user import UserUpdateDTO


class UserRepo(BaseRepository):
    async def get(self, user_id: UUID) -> UserDTO | None:
        query = select(User).where(User.id == user_id)
        user = await self._session.scalar(query)
        if user is None:
            return None

        return to_user_dto(user)

    async def get_by_telegram_user_id(
        self,
        telegram_user_id: int,
    ) -> UserDTO | None:
        query = select(User).where(User.telegram_user_id == telegram_user_id)
        user = await self._session.scalar(query)
        if user is None:
            return None

        return to_user_dto(user)

    async def create(
        self,
        dto: UserCreateDTO,
    ) -> UserDTO:
        user = User(
            telegram_user_id=dto.telegram_user_id,
            current_avatar_id=dto.current_avatar_id,
            active_chat_id=dto.active_chat_id,
        )
        self._session.add(user)
        await self._session.flush()

        return to_user_dto(user)

    async def update_user(
        self,
        user_id: UUID,
        dto: UserUpdateDTO,
    ) -> UserDTO | None:
        query = select(User).where(User.id == user_id)
        user = await self._session.scalar(query)
        if user is None:
            return None

        apply_user_update_dto(user=user, dto=dto)
        await self._session.flush()

        return to_user_dto(user)
