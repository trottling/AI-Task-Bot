import logging
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

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

@router.message(Command("timezone"))
async def set_timezone_command(message: Message) -> None:
    args = message.text.split()
    if message.chat.type == "private":
        if len(args) == 2:
            tz = args[1]
            if tz.startswith("+") or tz.startswith("-"):
                try:
                    int(tz)
                    settings_service.set_timezone(message.from_user.id, tz)
                    await message.answer(f"Ваш часовой пояс установлен на UTC{tz}")
                    return
                except ValueError:
                    pass
            await message.answer("Некорректный формат. Пример: /timezone +3")
        else:
            await message.answer("Укажите зону: /timezone +3")
    else:
        if len(args) == 2:
            tz = args[1]
            if tz.startswith("+") or tz.startswith("-"):
                try:
                    int(tz)
                    settings_service.set_chat_timezone(message.chat.id, tz)
                    await message.answer(f"Часовой пояс чата установлен на UTC{tz}")
                    return
                except ValueError:
                    pass
            await message.answer("Некорректный формат. Пример: /timezone +3")
        else:
            await message.answer("Укажите зону: /timezone +3")
