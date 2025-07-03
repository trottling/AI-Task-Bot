import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.user import user_kb
from loader import ADMINS, db
from .settings import settings_command

logger = logging.getLogger(__name__)


async def start_command(message: Message) -> None:
    if message.chat.type != "private":
        chat_id = message.chat.id
        try:
            db.add_chat(chat_id=chat_id, title=message.chat.title or "")
        except Exception as e:
            logger.exception(f"Не удалось добавить чат в БД: {e}")

        if not db.has_chat_access(chat_id):
            await message.answer(f"🚫 У чата нет доступа к боту. Обратитесь к администратору.\nℹ️ ID чата:\n>{chat_id}", parse_mode="MarkdownV2")
            return

        await message.answer("✅ Бот активирован в чате")
        return

    full_name = message.from_user.full_name
    telegram_id = message.from_user.id

    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)
    except Exception as e:
        logger.exception(f"Не удалось добавить пользователя в БД: {e}")

    if telegram_id not in ADMINS and not db.has_access(telegram_id):
        await message.answer(f"🚫 У вас нет доступа к боту. Обратитесь к администратору.\nℹ️ Ваш ID: {telegram_id}")
        return

    await message.answer(text=f'👋 Привет, {full_name}, нажми "Помощь" чтобы понять как работает бот', reply_markup=user_kb)


async def help_command(message: Message) -> None:
    await message.answer(
        "ℹ️ Бот создаёт задачи для календаря из сообщения\n\n"
        "1) Отправляете боту сообщение с задачей, например:\n"
        "20 января, вождение в 10 часов, с собой взять паспорт\n\n"
        "* Для создания задач в чате используйте команду /create\n\n"
        "2) Открываете файлы, которые прислал бот и добавляете мероприятия в любой календарь - на Android, IPhone или ПК\n\n"
        "Подробная инструкция по работе с ответами на частые вопросы:\nhttps://telegra.ph/111-07-01-32",
        reply_markup=user_kb
        )


async def settings_menu_command(message: Message, state: FSMContext):
    await settings_command(message, state)


async def create_command(message: Message, state: FSMContext):
    from .ics import start_ics_creation
    await start_ics_creation(message, state)
