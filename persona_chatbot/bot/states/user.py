from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class UserState(StatesGroup):
    choosing_avatar = State()
    chatting = State()
