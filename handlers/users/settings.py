import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

from loader import db

logger = logging.getLogger(__name__)


class Setup(StatesGroup):
    waiting_for_language = State()
    waiting_for_timezone = State()
    waiting_for_colors = State()


async def ask_language(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Русский"), KeyboardButton(text="English")]],
        resize_keyboard=True,
    )
    await message.answer(_("Выберите язык"), reply_markup=kb)
    await state.set_state(Setup.waiting_for_language)


async def set_language(message: Message, state: FSMContext) -> None:
    lang = "ru" if message.text.lower().startswith("рус") else "en"
    await state.update_data(language=lang)
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(text="UTC"), KeyboardButton(text="Europe/Moscow")]],
    )
    await message.answer(_("Выберите часовой пояс (например, Europe/Moscow или UTC)"), reply_markup=kb)
    await state.set_state(Setup.waiting_for_timezone)


async def set_timezone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "ru")
    tz = message.text.strip()
    db.set_settings(message.from_user.id, language=lang, timezone=tz)
    await state.clear()
    await message.answer(_("Настройки сохранены"), reply_markup=None)


async def settings_command(message: Message, state: FSMContext) -> None:
    await ask_language(message, state)

