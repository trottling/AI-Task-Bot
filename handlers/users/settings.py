import logging
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.user import user_kb
from loader import db
from services.settings_service import SettingsService

logger = logging.getLogger(__name__)

settings_service = SettingsService(db)
router = Router()

@router.message(lambda msg: msg.text == "⚙️ Настройки")
async def settings_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Нет доступных настроек.", reply_markup=user_kb)
