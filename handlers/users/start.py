import logging
from aiogram.types import Message

from keyboards.user import user_kb
from loader import ADMINS, db

logger = logging.getLogger(__name__)


async def start_command(message: Message) -> None:
    if message.chat.type != "private":
        chat_id = message.chat.id
        try:
            db.add_chat(chat_id=chat_id, title=message.chat.title or "")
        except Exception:
            logger.exception("Не удалось добавить чат в БД")

        if not db.has_chat_access(chat_id):
            await message.answer(
                "🚫 У чата нет доступа к боту. Обратитесь к администратору."
            )
            return

        await message.answer("✅ Бот активирован в чате")
        return

    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)
    except Exception:
        logger.exception("Не удалось добавить пользователя в БД")

    if telegram_id not in ADMINS and not db.has_access(telegram_id):
        await message.answer(
            "🚫 У вас нет доступа к боту. Обратитесь к администратору."
        )
        return

    await message.answer(
        text=f"👋 Привет, {full_name}, нажми Помощь чтобы понять как работает бот",
        reply_markup=user_kb,
    )
