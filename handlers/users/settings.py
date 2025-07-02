import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from loader import db

logger = logging.getLogger(__name__)


class Setup(StatesGroup):
    waiting_for_timezone = State()
    waiting_for_colors = State()


async def ask_timezone(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(text="UTC"), KeyboardButton(text="Europe/Moscow")]],
    )
    await message.answer(
        "Выберите часовой пояс (например, Europe/Moscow или UTC)",
        reply_markup=kb,
    )
    await state.set_state(Setup.waiting_for_timezone)


async def set_timezone(message: Message, state: FSMContext) -> None:
    tz = message.text.strip()
    db.set_settings(message.from_user.id, timezone=tz)
    await state.clear()
    await message.answer("Настройки сохранены", reply_markup=None)


async def settings_command(message: Message, state: FSMContext) -> None:
    await ask_timezone(message, state)

