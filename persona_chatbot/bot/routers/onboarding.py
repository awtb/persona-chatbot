from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from persona_chatbot.bot.keyboards import build_avatar_keyboard
from persona_chatbot.bot.states import UserState
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService

router = Router(name=__name__)


async def _start_avatar_selection(
    message: Message,
    user_service: UserService,
    state: FSMContext,
) -> None:
    avatars = await user_service.list_available_avatars()
    await state.set_state(UserState.choosing_avatar)
    if not avatars:
        await message.answer(
            "No avatars are available yet. Please try again later.",
        )
        return

    await message.answer(
        "Please choose an avatar to start chatting:",
        reply_markup=build_avatar_keyboard(avatars=avatars),
    )


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
        await _start_avatar_selection(
            message=message,
            user_service=user_service,
            state=state,
        )
        return

    await _resume_chat(
        message=message,
        state=state,
    )
