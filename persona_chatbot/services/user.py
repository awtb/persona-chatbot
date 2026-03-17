from datetime import datetime
from datetime import timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from persona_chatbot.common.enums import ChatStatus
from persona_chatbot.common.exceptions import AvatarNotSelected
from persona_chatbot.common.exceptions import UserNotFound
from persona_chatbot.db.repos.avatar import AvatarRepo
from persona_chatbot.db.repos.chat import ChatRepo
from persona_chatbot.db.repos.user import UserRepo
from persona_chatbot.dto.avatar import AvatarDTO
from persona_chatbot.dto.chat import ChatCreateDTO
from persona_chatbot.dto.chat import ChatUpdateDTO
from persona_chatbot.dto.user import UserCreateDTO
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.dto.user import UserUpdateDTO


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._user_repo = UserRepo(session=session)
        self._avatar_repo = AvatarRepo(session=session)
        self._chat_repo = ChatRepo(session=session)

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

    async def list_available_avatars(
        self,
    ) -> list[AvatarDTO]:
        return await self._avatar_repo.list_all()

    async def select_avatar(
        self,
        current_user: UserDTO,
        avatar_id: UUID,
    ) -> AvatarDTO:
        avatar = await self._avatar_repo.get(avatar_id=avatar_id)
        await self._start_new_chat(
            current_user=current_user,
            avatar_id=avatar_id,
        )
        return avatar

    async def reset_chat_context(
        self,
        current_user: UserDTO,
    ) -> UserDTO:
        if current_user.current_avatar_id is None:
            raise AvatarNotSelected()

        return await self._start_new_chat(
            current_user=current_user,
            avatar_id=current_user.current_avatar_id,
        )

    async def _start_new_chat(
        self,
        current_user: UserDTO,
        avatar_id: UUID,
    ) -> UserDTO:
        await self._close_active_chat_if_present(
            current_user=current_user,
        )
        chat = await self._chat_repo.create(
            dto=ChatCreateDTO(
                user_id=current_user.id,
                avatar_id=avatar_id,
            ),
        )
        updated_user = await self._user_repo.update_user(
            user_id=current_user.id,
            dto=UserUpdateDTO(
                telegram_user_id=current_user.telegram_user_id,
                current_avatar_id=avatar_id,
                active_chat_id=chat.id,
            ),
        )
        if updated_user is None:
            raise UserNotFound(
                telegram_user_id=current_user.telegram_user_id,
            )

        return updated_user

    async def _close_active_chat_if_present(
        self,
        current_user: UserDTO,
    ) -> None:
        if current_user.active_chat_id is None:
            return

        active_chat = await self._chat_repo.get(
            chat_id=current_user.active_chat_id,
        )
        await self._chat_repo.update_chat(
            chat_id=active_chat.id,
            dto=ChatUpdateDTO(
                user_id=active_chat.user_id,
                avatar_id=active_chat.avatar_id,
                status=ChatStatus.CLOSED,
                message_count=active_chat.message_count,
                completed_turn_count=active_chat.completed_turn_count,
                closed_at=active_chat.closed_at or datetime.now(timezone.utc),
            ),
        )
