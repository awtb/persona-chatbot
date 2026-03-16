from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from persona_chatbot.bot.callbacks import AVATAR_SELECT_CALLBACK_PREFIX
from persona_chatbot.bot.callbacks import parse_avatar_select_callback_data
from persona_chatbot.bot.states import UserState
from persona_chatbot.common.exceptions import AvatarNotFound
from persona_chatbot.dto.user import UserDTO
from persona_chatbot.services.user import UserService

router = Router(name=__name__)


@router.callback_query(
    UserState.choosing_avatar,
    F.data.startswith(AVATAR_SELECT_CALLBACK_PREFIX),
)
async def select_avatar(
    callback_query: CallbackQuery,
    current_user: UserDTO,
    user_service: UserService,
    state: FSMContext,
) -> None:
    avatar_id = parse_avatar_select_callback_data(
        callback_data=callback_query.data,
    )
    if avatar_id is None:
        await callback_query.answer(
            "Invalid avatar selection.",
            show_alert=True,
        )
        return

    try:
        await user_service.select_avatar(
            current_user=current_user,
            avatar_id=avatar_id,
        )
    except AvatarNotFound:
        await callback_query.answer(
            "Selected avatar does not exist.",
            show_alert=True,
        )
        return

    await state.set_state(UserState.chatting)
    await callback_query.answer("Avatar selected.")
    if callback_query.message is not None:
        await callback_query.message.answer(
            "Avatar selected. Send a message to start chatting.",
        )
