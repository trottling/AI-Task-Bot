import logging
from aiogram.types import Message

from keyboards.user import user_kb
from loader import db

logger = logging.getLogger(__name__)


async def start_command(message: Message) -> None:
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)
    except Exception:
        logger.exception("Не удалось добавить пользователя в БД")
    await message.answer(
        text=f"👋 Привет, {full_name}, нажми Помощь чтобы понять как работает бот",
        reply_markup=user_kb,
    )
