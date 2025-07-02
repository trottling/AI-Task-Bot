import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from keyboards.user import user_kb
from loader import ADMINS, db
from .settings import Setup, ask_language

logger = logging.getLogger(__name__)


async def start_command(message: Message, state: FSMContext) -> None:
    if message.chat.type != "private":
        chat_id = message.chat.id
        try:
            db.add_chat(chat_id=chat_id, title=message.chat.title or "")
        except Exception:
            logger.exception("Не удалось добавить чат в БД")

        if not db.has_chat_access(chat_id):
            await message.answer(
                _("🚫 У чата нет доступа к боту. Обратитесь к администратору.")
            )
            return

        await message.answer(_("✅ Бот активирован в чате"))
        return

    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)
    except Exception:
        logger.exception("Не удалось добавить пользователя в БД")

    if telegram_id not in ADMINS and not db.has_access(telegram_id):
        await message.answer(
            _("🚫 У вас нет доступа к боту. Обратитесь к администратору.")
        )
        return

    if not db.get_settings(telegram_id):
        await ask_language(message, state)
        return

    await message.answer(
        text=_("👋 Привет, {full_name}, нажми Помощь чтобы понять как работает бот").format(full_name=full_name),
        reply_markup=user_kb,
    )
