from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from persona_chatbot.bot.routers.avatar import show_avatar_selection
from persona_chatbot.bot.states import UserState
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService

router = Router(name=__name__)


async def _resume_chat(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(UserState.chatting)
    await message.answer("You can continue chatting.")


@router.message(CommandStart())
async def start(
    message: Message,
    current_user: UserDTO,
    user_service: UserService,
    state: FSMContext,
) -> None:
    if current_user.current_avatar_id is None:
        await show_avatar_selection(
            message=message,
            user_service=user_service,
            state=state,
        )
        return

    await _resume_chat(
        message=message,
        state=state,
    )
